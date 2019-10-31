/**
 * A minimal HTTP server that uses Mozilla’s Readability fork (the best working
 * and most maintained thing I could find) to convert the contets of a URL to
 * plain text.
 *
 * Make a request to `/proxy?url={some_url}` and it will return a plain-text
 * version of the main body of the content at `some_url`.
 *
 * NOTE: Readability is wrapped in a worker pool implementation because it is
 * not async. It is also not published as a standalone package on NPM, so we
 * depend directly on its git URL. See the source here:
 * https://github.com/mozilla/readability/
 */
'use strict';

const AbortController = require('abort-controller');
const express = require('express');
const fetch = require('node-fetch');
const WorkerPool = require('./worker-pool');

const serverPort = process.env.PORT || 7323;

const workerPool = new WorkerPool('./readability-worker.js', 10);
const app = express();

// The app provides only one endpoint: /proxy, which takes a URL and responds
// with the Readability-parsed text of the content at that URL.
app.get('/proxy', async function (thisRequest, response) {
  const url = thisRequest.query.url;
  if (!url) {
    return response.status(400).json({
      error: 'You must set the `?url=<url>` querystring parameter.'
    });
  }

  console.log('Proxying', url);

  try {
    const upstream = await timedFetch(url);
    const html = await upstream.text();
    const text = await workerPool.send({timeout: 10000}, html, url);
    if (text) {
      response
        .type('text/plain')
        .send(text);
    }
    else {
      response
        .status(422)
        .json({error: `Could not parse content at ${url}`});
    }
  }
  catch (error) {
    if (error.name === 'AbortError') {
      response.status(504).json({error: `Upstream request timed out: ${url}`});
      console.error('TIMEOUT:', url);
    }
    else {
      response.status(500).json({error: error.message});
      console.error(error);
      console.error('  While processing:', url);
    }
  }
});

function timedFetch (url, options = {}) {
  const timeout = options.totalTimeout || (options.timeout * 2) || 10000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  options = Object.assign({signal: controller.signal}, options);
  return fetch(url, options).finally(() => clearTimeout(timer));
}

app.listen(serverPort, function () {
  console.log(`Listening on port ${serverPort}`);
});
