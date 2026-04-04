#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

// ── Rule sets ────────────────────────────────────────────────────────────────

const KNOWN_PREPS = new Set([
  'auf', 'aus', 'bei', 'bis', 'durch', 'für', 'gegen', 'in', 'mit', 'nach',
  'von', 'zu', 'über', 'unter', 'an', 'bar', 'um', 'ohne', 'seit', 'ab',
  'gegenüber',
]);

const ADJ_SUFFIXES = ['lich', 'ig', 'isch', 'sam', 'los', 'bar'];

// Adverbs listed by the user
const ADV_WORDS = new Set([
  'bald', 'gestern', 'heute', 'hier', 'dort', 'gerade', 'immer', 'jetzt',
  'gleich', 'noch', 'schon', 'auch', 'dann', 'früher', 'hinten', 'hoch',
  'jung', 'kaputt', 'fremd', 'frei',
]);

// Pronouns listed by the user (hyphen entries match the literal de field, e.g. "dein-")
const PRON_WORDS = new Set([
  'ich', 'er', 'sie', 'es', 'wir', 'ihr', 'dich', 'dir', 'ihn', 'ihm',
  'beide', 'jed-', 'ein-', 'dein-', 'mein-', 'sein-', 'euer',
]);

const CONJ_WORDS = new Set(['denn', 'weil', 'aber', 'oder', 'und', 'sondern']);

const STANDALONE_ARTICLES = new Set(['das', 'der', 'die']);

// ── Main ─────────────────────────────────────────────────────────────────────

const filePath = path.join(__dirname, 'vocab.json');
const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

const stats = { changed: 0, removed: 0 };
const log = [];

function reclassify(entry, newType, reason) {
  log.push(`  [${entry.type} → ${newType}] "${entry.de}" (${entry.en}) — ${reason}`);
  stats.changed++;
  return { ...entry, type: newType };
}

const result = [];

for (const entry of data) {
  const deKey = (entry.de || '').toLowerCase().trim();
  const en    = entry.en || '';
  const type  = entry.type;

  // Rule 5: Remove standalone articles
  if (STANDALONE_ARTICLES.has(deKey)) {
    log.push(`  [REMOVED] "${entry.de}" (${entry.en})`);
    stats.removed++;
    continue;
  }

  if (type === 'prep') {
    // Rule 1: Known preposition → keep as-is
    if (KNOWN_PREPS.has(deKey)) {
      result.push(entry);
      continue;
    }

    // Rule 2: Adj suffix → adj
    if (ADJ_SUFFIXES.some(suf => deKey.endsWith(suf))) {
      result.push(reclassify(entry, 'adj', `ends in adj suffix`));
      continue;
    }

    // Rule 3: No article + English starts with "to " → verb
    if (!entry.article && en.startsWith('to ')) {
      result.push(reclassify(entry, 'verb', `no article and English starts with "to "`));
      continue;
    }

    // No rule matched — leave unchanged
    result.push(entry);
    continue;
  }

  if (type === 'verb') {
    // Rule 4: English doesn't start with "to " → attempt reclassification
    if (!en.startsWith('to ')) {
      if (ADV_WORDS.has(deKey)) {
        result.push(reclassify(entry, 'adv', `listed adverb`));
        continue;
      }
      if (PRON_WORDS.has(deKey)) {
        result.push(reclassify(entry, 'pron', `listed pronoun`));
        continue;
      }
      if (CONJ_WORDS.has(deKey)) {
        result.push(reclassify(entry, 'conj', `listed conjunction`));
        continue;
      }
    }

    result.push(entry);
    continue;
  }

  result.push(entry);
}

// ── Report ───────────────────────────────────────────────────────────────────

console.log(`Before: ${data.length} entries`);
console.log(`After:  ${result.length} entries`);
console.log(`Removed: ${stats.removed}   Changed type: ${stats.changed}\n`);

if (log.length) {
  console.log('Changes:');
  log.forEach(l => console.log(l));
}

// ── Write ─────────────────────────────────────────────────────────────────────

fs.writeFileSync(filePath, JSON.stringify(result, null, 2), 'utf8');
console.log(`\nWrote ${filePath}`);
