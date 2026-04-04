const fs = require('fs');
const vocab = JSON.parse(fs.readFileSync('vocab.json', 'utf8'));

const adverbs = new Set(['auch','bald','da','dann','dort','dorthin','dorther','draußen','früher','gerade','geradeaus','gleich','hallo','heute','hier','hinten','hoch','immer','jetzt','jung','kaputt','schon','noch','daneben','danke','circa/ca.','fremd','frei']);
const pronouns = new Set(['beide','dein-','dies-','ein-','jed-','euer','er','es','ich','dich','dir','ihn','ihm/ihr']);
const adjectives = new Set(['bekannt','besetzt','besser','best-','bitter','böse','breit','einfach','falsch','frei','fremd','gleich','groß','gut','hoch','jung','kaputt']);
const conjunctions = new Set(['denn','weil','aber','oder','und','sondern','doch']);
const removeWords = new Set(['das','der','die','bisschen','bis','daneben','gestern','gestorben','geboren','gegen']);

const fixed = vocab.filter(c => {
  const base = c.de.trim().toLowerCase();
  if (removeWords.has(base)) return false;
  return true;
}).map(c => {
  const base = c.de.trim().toLowerCase();
  if (c.type === 'prep' || c.type === 'verb') {
    if (adjectives.has(base)) c.type = 'adj';
    else if (pronouns.has(base)) c.type = 'pron';
    else if (adverbs.has(base)) c.type = 'adv';
    else if (conjunctions.has(base)) c.type = 'conj';
    else if (!c.en.startsWith('to ') && c.type === 'verb' && !c.article) c.type = 'adv';
  }
  return c;
});

fs.writeFileSync('vocab.json', JSON.stringify(fixed, null, 2));
console.log('Done. Entries:', fixed.length);
