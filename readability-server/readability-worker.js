const JSDOM = require('jsdom').JSDOM;
const Readability = require('readability');
const WorkerPool = require('./worker-pool');

WorkerPool.implementWorker((html, url) => {
  const dom = new JSDOM(html, { url });
  const reader = new Readability(dom.window.document);
  const article = reader.parse();

  if (article) return `${article.title}\n\n${article.textContent}`;
  else return null;
});
