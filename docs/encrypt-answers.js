#!/usr/bin/env node
/**
 * 解答セクションを AES-256-GCM で暗号化するビルドスクリプト
 *
 * 使い方:
 *   node encrypt-answers.js <password> <file.html> [file2.html ...]
 *   node encrypt-answers.js <password> --all   # week*.html を一括処理
 *
 * 処理:
 *   1. <div id="answers-content"> 〜 対応する閉じタグの中身を抽出
 *   2. PBKDF2 (100,000 rounds) + AES-256-GCM で暗号化
 *   3. 暗号文を base64 で <div id="answers-encrypted" data-cipher="..."> に置換
 *   4. 元ファイルを上書き保存
 */
'use strict';

const crypto = require('crypto');
const fs     = require('fs');
const path   = require('path');
const glob   = require('path');

// ── 暗号パラメータ ──
const PBKDF2_ITERATIONS = 100_000;
const KEY_LEN           = 32; // AES-256
const SALT_LEN          = 16;
const IV_LEN            = 12; // GCM recommended

function encrypt(plaintext, password) {
  const salt = crypto.randomBytes(SALT_LEN);
  const key  = crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, KEY_LEN, 'sha256');
  const iv   = crypto.randomBytes(IV_LEN);

  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const enc    = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const tag    = cipher.getAuthTag(); // 16 bytes

  // salt(16) + iv(12) + tag(16) + ciphertext → base64
  return Buffer.concat([salt, iv, tag, enc]).toString('base64');
}

function processFile(filePath, password) {
  let html = fs.readFileSync(filePath, 'utf8');

  // <div id="answers-content"> の開始位置を探す
  const startMarker = '<div id="answers-content">';
  const startIdx = html.indexOf(startMarker);
  if (startIdx === -1) {
    console.log(`  SKIP: ${filePath} (answers-content not found)`);
    return false;
  }

  // 既に暗号化済みかチェック
  if (html.indexOf('id="answers-encrypted"') !== -1) {
    console.log(`  SKIP: ${filePath} (already encrypted)`);
    return false;
  }

  // 対応する閉じ </div> を探す（ネスト対応）
  const contentStart = startIdx + startMarker.length;
  let depth = 1;
  let pos = contentStart;
  while (depth > 0 && pos < html.length) {
    const nextOpen  = html.indexOf('<div', pos);
    const nextClose = html.indexOf('</div>', pos);
    if (nextClose === -1) break;
    if (nextOpen !== -1 && nextOpen < nextClose) {
      depth++;
      pos = nextOpen + 4;
    } else {
      depth--;
      if (depth === 0) {
        // pos は最後の </div> の位置
        const innerHtml = html.substring(contentStart, nextClose).trim();
        const cipherB64 = encrypt(innerHtml, password);

        // 置換: answers-content div 全体を encrypted div に変える
        const oldBlock = html.substring(startIdx, nextClose + 6); // </div> = 6 chars
        const newBlock = '<div id="answers-encrypted" data-cipher="' + cipherB64 + '"></div>';
        html = html.replace(oldBlock, newBlock);

        fs.writeFileSync(filePath, html, 'utf8');
        console.log(`  OK: ${filePath} (${innerHtml.length} chars → ${cipherB64.length} chars base64)`);
        return true;
      } else {
        pos = nextClose + 6;
      }
    }
  }

  console.log(`  ERR: ${filePath} (could not find matching </div>)`);
  return false;
}

// ── メイン ──
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node encrypt-answers.js <password> <file.html ...>');
  console.error('       node encrypt-answers.js <password> --all');
  process.exit(1);
}

const password = args[0];
let files = args.slice(1);

if (files[0] === '--all') {
  const dir = path.dirname(__filename);
  files = fs.readdirSync(dir)
    .filter(f => /^week\d+\.html$/.test(f))
    .map(f => path.join(dir, f));
}

console.log(`Encrypting ${files.length} file(s) with PBKDF2+AES-256-GCM ...`);
let count = 0;
for (const f of files) {
  const resolved = path.resolve(f);
  if (processFile(resolved, password)) count++;
}
console.log(`Done: ${count} file(s) encrypted.`);
