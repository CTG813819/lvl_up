// check-proposal-fields.js
const fs = require('fs');
const path = require('path');

const SRC_DIR = path.join(__dirname, 'src');
const REQUIRED_FIELDS = [
  'codeBefore',
  'codeAfter',
  'aiType',
  'filePath',
  'reasoning',
  'improvementType',
];

function getAllJsFiles(dir) {
  let results = [];
  fs.readdirSync(dir).forEach(file => {
    const full = path.join(dir, file);
    if (fs.statSync(full).isDirectory()) {
      results = results.concat(getAllJsFiles(full));
    } else if (file.endsWith('.js')) {
      results.push(full);
    }
  });
  return results;
}

// Helper to extract object literal from code, even if multi-line and nested
function extractObjectLiteral(lines, startIdx, startPos) {
  let obj = '';
  let open = 0;
  let started = false;
  let spreadDetected = false;
  for (let i = startIdx; i < lines.length; i++) {
    let line = lines[i].slice(i === startIdx ? startPos : 0);
    for (let j = 0; j < line.length; j++) {
      const char = line[j];
      if (char === '{') {
        open++;
        started = true;
      }
      if (started) obj += char;
      // Detect spread syntax
      if (started && line[j] === '.' && line[j+1] === '.' && line[j+2] === '.') {
        spreadDetected = true;
      }
      if (char === '}') {
        open--;
        if (open === 0 && started) {
          return { obj, endIdx: i, spreadDetected };
        }
      }
    }
    if (started) obj += '\n';
  }
  return { obj: '', endIdx: startIdx, spreadDetected };
}

function isObjectLiteral(str) {
  // Simple check: starts with { and ends with }
  return str.trim().startsWith('{') && str.trim().endsWith('}');
}

function parseObjectLiteral(objStr) {
  // Very basic parse: get top-level keys (does not handle nested objects well)
  const keys = [];
  let key = '';
  let inKey = true;
  let inString = false;
  let stringChar = '';
  let depth = 0;
  for (let i = 0; i < objStr.length; i++) {
    const char = objStr[i];
    if (inString) {
      if (char === stringChar) inString = false;
      continue;
    }
    if (char === '"' || char === "'") {
      inString = true;
      stringChar = char;
      continue;
    }
    if (char === '{') { depth++; continue; }
    if (char === '}') { depth--; continue; }
    if (depth > 1) continue;
    if (inKey && /[a-zA-Z0-9_]/.test(char)) {
      key += char;
    } else if (inKey && char === ':') {
      if (key) keys.push(key.trim());
      key = '';
      inKey = false;
    } else if (!inKey && char === ',') {
      inKey = true;
    }
  }
  return keys;
}

function autoFixFile(file) {
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split('\n');
  let changed = false;
  let changes = [];
  let newLines = [...lines];

  lines.forEach((line, idx) => {
    // Patterns to match creation points
    const patterns = [
      { regex: /new\s+Proposal\s*\((.*)/g, type: 'new' },
      { regex: /Proposal\.create\s*\((.*)/g, type: 'create' },
      { regex: /Proposal\.insertMany\s*\((.*)/g, type: 'insertMany' },
    ];
    patterns.forEach(({ regex, type }) => {
      let match;
      while ((match = regex.exec(line)) !== null) {
        const afterParen = match[1];
        if (afterParen.trim().startsWith('{')) {
          const startPos = match.index + match[0].length - afterParen.length;
          const { obj, endIdx, spreadDetected } = extractObjectLiteral(lines, idx, startPos);
          const presentKeys = parseObjectLiteral(obj);
          const missing = REQUIRED_FIELDS.filter(f => !presentKeys.includes(f));
          if (missing.length > 0) {
            changed = true;
            // Insert missing fields before the closing }
            let fixedObj = obj.trim();
            if (fixedObj.endsWith('}')) fixedObj = fixedObj.slice(0, -1);
            let suggestions = '';
            missing.forEach(f => {
              suggestions += `  ${f}: 'FIXME_${f}',\n`;
            });
            // Remove trailing comma if present
            fixedObj = fixedObj.replace(/,?\s*$/, '');
            const fixedCode = `${fixedObj},\n${suggestions}}`;
            // Replace lines in newLines
            const before = newLines.slice(idx, endIdx + 1).join('\n');
            newLines.splice(idx, endIdx - idx + 1, ...fixedCode.split('\n'));
            changes.push({
              file,
              line: idx + 1,
              before,
              after: fixedCode,
              added: missing,
            });
          }
        }
      }
    });
  });

  if (changed) {
    // Backup original file
    fs.copyFileSync(file, file + '.bak');
    fs.writeFileSync(file, newLines.join('\n'), 'utf8');
  }
  return changes;
}

function checkFile(file) {
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split('\n');
  const results = [];
  let total = 0, objectLiterals = 0, dynamic = 0, missingFields = 0;

  lines.forEach((line, idx) => {
    // Patterns to match creation points
    const patterns = [
      { regex: /new\s+Proposal\s*\((.*)/g, type: 'new' },
      { regex: /Proposal\.create\s*\((.*)/g, type: 'create' },
      { regex: /Proposal\.insertMany\s*\((.*)/g, type: 'insertMany' },
    ];
    patterns.forEach(({ regex, type }) => {
      let match;
      while ((match = regex.exec(line)) !== null) {
        total++;
        const afterParen = match[1];
        if (afterParen.trim().startsWith('{')) {
          const startPos = match.index + match[0].length - afterParen.length;
          const { obj, endIdx, spreadDetected } = extractObjectLiteral(lines, idx, startPos);
          objectLiterals++;
          const presentKeys = parseObjectLiteral(obj);
          const missing = REQUIRED_FIELDS.filter(f => !presentKeys.includes(f));
          if (missing.length > 0) {
            missingFields++;
            let fixedObj = obj.trim();
            if (fixedObj.endsWith('}')) fixedObj = fixedObj.slice(0, -1);
            let suggestions = '';
            missing.forEach(f => {
              suggestions += `  ${f}: 'FIXME_${f}',\n`;
            });
            fixedObj = fixedObj.replace(/,?\s*$/, '');
            const fixedCode = `${fixedObj},\n${suggestions}}`;
            results.push({
              file,
              line: idx + 1,
              code: lines.slice(idx, endIdx + 1).join('\n').trim(),
              missing,
              type: 'object-literal',
              spread: spreadDetected,
              fixedCode,
            });
          } else {
            results.push({
              file,
              line: idx + 1,
              code: lines.slice(idx, endIdx + 1).join('\n').trim(),
              missing: [],
              type: 'object-literal',
              spread: spreadDetected,
            });
          }
        } else {
          dynamic++;
          let arg = afterParen.split(',')[0].split(')')[0].trim();
          results.push({
            file,
            line: idx + 1,
            code: line.trim(),
            missing: ['unknown (dynamic argument)'],
            type: 'dynamic',
            spread: false,
            arg,
          });
        }
      }
    });
  });

  return { results, stats: { total, objectLiterals, dynamic, missingFields } };
}

function main() {
  const files = getAllJsFiles(SRC_DIR);
  let allResults = [];
  let total = 0, objectLiterals = 0, dynamic = 0, missingFields = 0;
  let allChanges = [];
  files.forEach(file => {
    const changes = autoFixFile(file);
    if (changes.length > 0) {
      allChanges = allChanges.concat(changes);
    }
    const { results, stats } = checkFile(file);
    allResults = allResults.concat(results);
    total += stats.total;
    objectLiterals += stats.objectLiterals;
    dynamic += stats.dynamic;
    missingFields += stats.missingFields;
  });

  if (allResults.length === 0) {
    console.log('✅ No proposal creation points found.');
    return;
  }

  console.log('--- Proposal Creation Points Audit ---');
  allResults.forEach(r => {
    console.log(`File: ${r.file}, Line: ${r.line}`);
    console.log(`  Type: ${r.type}`);
    if (r.type === 'dynamic') {
      console.log(`  Argument: ${r.arg}`);
      console.log('  ⚠️  Cannot statically check required fields for dynamic argument. Please audit manually.');
    } else {
      if (r.spread) {
        console.log('  ⚠️  Spread syntax detected in object. Please audit manually for required fields.');
      }
      if (r.missing.length > 0) {
        console.log(`  ❌ Missing fields: ${r.missing.join(', ')}`);
        console.log('  💡 Suggested fixed code block:');
        console.log(r.fixedCode);
      } else {
        console.log('  ✅ All required fields present.');
      }
    }
    console.log(`  Code:\n${r.code}`);
    console.log('---');
  });
  if (allChanges.length > 0) {
    console.log('--- Auto-fix Summary ---');
    allChanges.forEach(change => {
      console.log(`File: ${change.file}, Line: ${change.line}`);
      console.log(`  Added fields: ${change.added.join(', ')}`);
      console.log('  Before:');
      console.log(change.before);
      console.log('  After:');
      console.log(change.after);
      console.log('---');
    });
    console.log('Backup of original files saved as .bak');
  }
  console.log('--- Summary ---');
  console.log(`Total proposal creation points: ${total}`);
  console.log(`  Object literals: ${objectLiterals}`);
  console.log(`  Dynamic arguments: ${dynamic}`);
  console.log(`  With missing required fields: ${missingFields}`);
  console.log('----------------');
}

main(); 