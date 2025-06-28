const archiver = require('archiver');
const fs = require('fs');
const path = require('path');

// Create a file to stream archive data to
const output = fs.createWriteStream(path.join(__dirname, '../ai-learning-backend.zip'));
const archive = archiver('zip', {
  zlib: { level: 9 } // Sets the compression level
});

// Listen for all archive data to be written
output.on('close', function() {
  console.log('Archive created successfully!');
  console.log('Total size: ' + archive.pointer() + ' bytes');
});

// Good practice to catch warnings (ie stat failures and other non-blocking errors)
archive.on('warning', function(err) {
  if (err.code === 'ENOENT') {
    console.warn('Warning:', err);
  } else {
    throw err;
  }
});

// Good practice to catch this error explicitly
archive.on('error', function(err) {
  throw err;
});

// Pipe archive data to the file
archive.pipe(output);

// Add files to the archive
archive.file('package.json', { name: 'package.json' });
archive.file('package-lock.json', { name: 'package-lock.json' });
archive.directory('src/', 'src/');
archive.directory('uploads/', 'uploads/');

// Finalize the archive (ie we are done appending files but streams have to finish yet)
archive.finalize(); 