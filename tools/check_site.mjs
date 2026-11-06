import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { chromium } from 'playwright';

const base = 'http://127.0.0.1:8767';
const output = await fs.mkdtemp(path.join(os.tmpdir(), 'fengli-homepage-qa-'));
const browser = await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const errors = [];
try {
  const context = await browser.newContext({viewport:{width:1440,height:1050}});
  await context.grantPermissions(['clipboard-read','clipboard-write'],{origin:base});
  const page = await context.newPage();
  page.on('pageerror',error=>errors.push(error.message));
  page.on('response',response=>{if(response.status()>=400 && response.url().startsWith(base)) errors.push(`${response.status()} ${response.url()}`);});
  await page.goto(base,{waitUntil:'networkidle'});
  assert.equal(await page.locator('h1').count(),1);
  assert.ok(await page.getByRole('heading',{name:'About me',exact:true}).isVisible());
  assert.equal(await page.locator('.publication').count(),5);
  assert.equal(await page.locator('.cv-links, a[href*="assets/cv/"]').count(),0);
  assert.equal(await page.locator('a[href*="github.com/FonX1997"]').count(),0);
  assert.ok(await page.locator('.portrait').evaluate(image=>image.complete && image.naturalWidth>0));
  assert.ok(await page.locator('.university-seal').evaluate(image=>image.complete && image.naturalWidth>0));
  await page.screenshot({path:path.join(output,'desktop-home.png'),fullPage:true});
  await page.screenshot({path:path.join(output,'desktop-home-first-screen.png')});
  await page.getByRole('button',{name:'切换为中文'}).click();
  assert.ok(await page.getByRole('heading',{name:'关于我',exact:true}).isVisible());
  await page.getByRole('link',{name:'科研',exact:true}).click();
  assert.equal(await page.locator('html').getAttribute('lang'),'zh');
  assert.equal(await page.locator('.project').count(),4);
  assert.equal(await page.locator('a[href*="github.com/FonX1997"]').count(),0);
  assert.equal(await page.locator('.cv-links, a[href*="assets/cv/"]').count(),0);
  assert.ok((await page.locator('.project').nth(0).innerText()).includes('62603043'));
  assert.ok((await page.locator('.project').nth(1).innerText()).includes('杭州市软科学'));
  await page.screenshot({path:path.join(output,'desktop-research-zh.png'),fullPage:true});
  await page.getByRole('link',{name:'论文',exact:true}).click();
  assert.equal(await page.locator('#publication-list .publication').count(),14);
  assert.equal(await page.locator('a[href*="github.com/FonX1997"]').count(),0);
  assert.equal(await page.locator('.cv-links, a[href*="assets/cv/"]').count(),0);
  const search = page.locator('#publication-search');
  await search.fill('ANEU-TCN');
  assert.equal(await page.locator('#publication-list .publication:visible').count(),1);
  assert.equal(await page.locator('#publication-count').innerText(),'共 1 篇');
  await search.fill('');
  await page.locator('#publication-year').selectOption('2025');
  assert.equal(await page.locator('#publication-list .publication:visible').count(),3);
  await page.locator('#publication-year').selectOption('2027');
  assert.equal(await page.locator('#publication-list .publication:visible').count(),1);
  await page.locator('#publication-year').selectOption('all');
  await search.fill('no-such-publication');
  assert.ok(await page.locator('#no-results').isVisible());
  await search.fill('');
  const papers = await page.evaluate(()=>window.PUBLICATIONS);
  for(const paper of papers){
    await page.locator(`[data-bibtex="${paper.id}"]`).click();
    assert.ok(await page.locator('#bibtex-dialog').isVisible());
    const text = await page.locator('#bibtex-code').innerText();
    assert.ok(text.includes(paper.title));
    if(paper.doi) assert.ok(text.includes(paper.doi));
    if(paper.accepted) assert.ok(text.includes('Accepted for publication'));
    if(paper.id==='scis'){
      await page.locator('#copy-bibtex').click();
      await page.waitForFunction(()=>document.querySelector('#copy-status').textContent.includes('已复制'));
      assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).includes('10.1360/s11432-026-5050-y'));
    }
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#bibtex-dialog').isVisible(),false);
  }
  await page.getByRole('button',{name:'Read in English'}).click();
  assert.equal(await page.locator('#publication-count').innerText(),'14 papers');
  await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,0);document.activeElement?.blur();});
  await page.waitForFunction(()=>scrollY===0);
  await page.screenshot({path:path.join(output,'desktop-publications.png'),fullPage:true});
  const mobile = await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
  const phone = await mobile.newPage();
  phone.on('pageerror',error=>errors.push(error.message));
  for(const filename of ['index.html','research.html','publications.html']){
    await phone.goto(`${base}/${filename}`,{waitUntil:'networkidle'});
    await phone.getByRole('button',{name:'切换为中文'}).click();
    assert.ok(await phone.locator('.university-seal').evaluate(image=>image.complete && image.naturalWidth>0));
    const bounds = await phone.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth}));
    assert.ok(bounds.width<=bounds.viewport,JSON.stringify({filename,...bounds}));
    await phone.screenshot({path:path.join(output,`mobile-${filename.replace('.html','')}.png`),fullPage:true});
    if(filename==='index.html') await phone.screenshot({path:path.join(output,'mobile-home-first-screen.png')});
  }
  for(const width of [320,768,1024]){
    await phone.setViewportSize({width,height:900});
    for(const filename of ['index.html','research.html','publications.html']){
      await phone.goto(`${base}/${filename}`,{waitUntil:'networkidle'});
      for(const lang of ['en','zh']){
        await phone.locator(`[data-set-language="${lang}"]`).click();
        const bounds = await phone.evaluate(()=>({width:document.documentElement.scrollWidth,viewport:innerWidth}));
        assert.ok(bounds.width<=bounds.viewport,JSON.stringify({filename,lang,...bounds}));
      }
    }
  }
  for(const filename of ['assets/bibtex/Feng-Li-publications.bib']){
    const response = await context.request.get(`${base}/${filename}`);
    assert.equal(response.status(),200);
  }
  for(const filename of ['assets/cv/Feng-Li-CV.pdf','assets/cv/李峰-中文简历.pdf']){
    const response = await context.request.get(`${base}/${filename}`);
    assert.equal(response.status(),404);
  }
  assert.deepEqual(errors,[]);
  const results = {passed:true,pages:3,publications:papers.length,bibtexDialogsChecked:papers.length,acceptedPapers:papers.filter(p=>p.accepted).length,clipboard:true,languagePersistence:true,searchAndYearFilters:true,mobileOverflow:false,screenshots:output};
  await fs.writeFile(new URL('./qa-results.json',import.meta.url),JSON.stringify(results,null,2));
  console.log(JSON.stringify(results));
} finally { await browser.close(); }
