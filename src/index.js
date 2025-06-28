// Force immediate GitHub pull and scan after server start
(async () => {
  console.log('[AI-AUTO] Immediate GitHub pull and scan after server start...');
  await ensureRepoUpToDate();
  const files = getAllDartFiles(path.join(LOCAL_PATH, 'lib'));
  console.log(`[AI-AUTO] Found ${files.length} Dart files in repo.`);

  // Run Imperium
  try {
    console.log('[AI-AUTO] Imperium: Running immediate scan...');
    for (const filePath of files) {
      const code = fs.readFileSync(filePath, 'utf8');
      await runImperiumExperiment(code, filePath);
    }
    console.log('[AI-AUTO] Imperium scan complete.');
  } catch (e) {
    console.error('[AI-AUTO] Imperium error:', e);
  }

  // Run Sandbox
  try {
    console.log('[AI-AUTO] Sandbox: Running immediate scan...');
    for (const filePath of files) {
      const code = fs.readFileSync(filePath, 'utf8');
      await runSandboxExperiment(code, filePath);
    }
    console.log('[AI-AUTO] Sandbox scan complete.');
  } catch (e) {
    console.error('[AI-AUTO] Sandbox error:', e);
  }

  // Run Guardian
  try {
    console.log('[AI-AUTO] Guardian: Running immediate scan...');
    const missionFiles = files.filter(f => f.includes('mission'));
    for (const filePath of missionFiles) {
      const code = fs.readFileSync(filePath, 'utf8');
      await runGuardianExperiment(code, filePath);
    }
    console.log('[AI-AUTO] Guardian scan complete.');
  } catch (e) {
    console.error('[AI-AUTO] Guardian error:', e);
  }
})();

const analyticsRouter = require('./routes/analytics');
const notifyRouter = require('./routes/notify');
app.use('/api/analytics', analyticsRouter);
app.use('/api/notify', notifyRouter);

const PORT = process.env.PORT || 4000;
server.listen(PORT, '234.55.93.144', () => console.log(`Server running on 234.55.93.144:${PORT}`)); 