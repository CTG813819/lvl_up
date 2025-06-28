const express = require('express');
const router = express.Router();
const Experiment = require('../models/experiment');

router.post('/', async (req, res) => {
  const experiment = new Experiment(req.body);
  await experiment.save();
  res.json(experiment);
});

router.get('/', async (req, res) => {
  const experiments = await Experiment.find();
  res.json(experiments);
});

module.exports = router;