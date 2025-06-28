const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');

function getAllDartFiles(dir, files = []) {
  fs.readdirSync(dir).forEach(file => {
    const fullPath = path.join(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      getAllDartFiles(fullPath, files);
    } else if (file.endsWith('.dart')) {
      files.push(fullPath);
    }
  });
  return files;
}

async function uploadFiles(files) {
  const form = new FormData();
  files.forEach(file => {
    form.append('files', fs.createReadStream(file), path.basename(file));
  });
  try {
    const response = await axios.post('http://localhost:3000/api/code/upload', form, {
      headers: form.getHeaders(),
    });
    console.log('Upload response:', response.data);
  } catch (err) {
    console.error('Upload failed:', err.message);
  }
}

const dartFiles = getAllDartFiles(path.join(__dirname, '../lib'));
console.log('Found Dart files:', dartFiles);
uploadFiles(dartFiles); 