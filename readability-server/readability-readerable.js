/* eslint-env es6:false */
/* globals exports */

/* ---------------------------------------------------------------------------
 * THIS IS A FORK OF `Readability-readaberable.js` IN THE 'readability` PACKAGE
 * Changes are marked with `// EDGI:` and we should think about eventually
 * upstreaming them if we start to feel they are stable.
 * ------------------------------------------------------------------------ */

/*
 * Copyright (c) 2010 Arc90 Inc
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * This code is heavily based on Arc90's readability.js (1.7.1) script
 * available at: http://code.google.com/p/arc90labs-readability
 */

var REGEXPS = {
  // NOTE: These two regular expressions are duplicated in
  // Readability.js. Please keep both copies in sync.
  unlikelyCandidates: /-ad-|ai2html|banner|breadcrumbs|combx|comment|community|cover-wrap|disqus|extra|footer|gdpr|header|legends|menu|related|remark|replies|rss|shoutbox|sidebar|skyscraper|social|sponsor|supplemental|ad-break|agegate|pagination|pager|popup|yom-remote/i,
  okMaybeItsACandidate: /and|article|body|column|content|main|shadow/i,
};

function isNodeVisible(node) {
  // Have to null-check node.style to deal with SVG and MathML nodes.
  return (!node.style || node.style.display != "none") && !node.hasAttribute("hidden")
    && (!node.hasAttribute("aria-hidden") || node.getAttribute("aria-hidden") != "true");
}

// EDGI: Helpers since we may not have `Node` global (e.g. in Node.js)
function isTextNode(node) {
  return !!node && node.nodeType === node.TEXT_NODE;
}
function isElementNode(node) {
  return !!node && node.nodeType === node.ELEMENT_NODE;
}

/**
 * Decides whether or not the document is reader-able without parsing the whole thing.
 *
 * @return boolean Whether or not we suspect Readability.parse() will suceeed at returning an article object.
 */
function isProbablyReaderable(doc, isVisible) {
  if (!isVisible) {
    isVisible = isNodeVisible;
  }

  var nodes = doc.querySelectorAll("p, pre");

  // Get <div> nodes which have <br> node(s) and append them into the `nodes` variable.
  // Some articles' DOM structures might look like
  // <div>
  //   Sentences<br>
  //   <br>
  //   Sentences<br>
  // </div>
  var brNodes = doc.querySelectorAll("div > br");
  if (brNodes.length) {
    var set = new Set(nodes);
    [].forEach.call(brNodes, function(node) {
      set.add(node.parentNode);
    });
    nodes = Array.from(set);
  }

  // EDGI: Add list items that are mainly text, since they are like paragraphs.
  var listItems = doc.querySelectorAll("li, dd");
  listItems = Array.from(listItems).filter(function(node) {
    if (node.querySelector('div, p')) return false;
    var nonLinkText = Array.from(node.childNodes).filter(function(node) {
      if (!isTextNode(node) && !isElementNode(node)) return false;
      if (['A', 'OL', 'UL', 'DL'].includes(node.nodeName)) return false;
      if (node.data && !node.data.trim().length) return false;
      return true;
    });
    if (nonLinkText.length === 0) return false;
    // if (node.matches('nav *, .nav *, .menu *')) return false;
    return true;
  });
  if (listItems.length) nodes = Array.from(nodes).concat(listItems);

  var score = 0;
  // This is a little cheeky, we use the accumulator 'score' to decide what to return from
  // this callback:
  return [].some.call(nodes, function(node) {
    if (!isVisible(node))
      return false;

    var matchString = node.className + " " + node.id;
    if (REGEXPS.unlikelyCandidates.test(matchString) &&
        !REGEXPS.okMaybeItsACandidate.test(matchString)) {
      return false;
    }

    if (node.matches("li p") || node.matches('[class*="teaser"],[class*="related"]')) {
      return false;
    }

    var textContentLength = node.textContent.trim().length;
    if (textContentLength < 140) {
      return false;
    }

    score += Math.sqrt(textContentLength - 140);

    if (score > 20) {
      return true;
    }
    return false;
  });
}

if (typeof exports === "object") {
  exports.isProbablyReaderable = isProbablyReaderable;
}
