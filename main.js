const logEl = document.getElementById('log');
const precheckEl = document.getElementById('precheck');

const precheckItems = [
  'Review load chart, SWL, radius, and wind limits. Apply heel/trim corrections.',
  'Inspect wire rope, hook, sheaves, brakes, limit switches, and overload devices.',
  'Verify communication plan (UHF/VHF channel or hand signals) and exclusion zones.',
  'Check hydraulic oil level, temperature, accumulator pre-charge, and brake pressure.',
  'Confirm deck is clear, load is rigged with certified gear, and route is free of obstructions.',
];

const crane = {
  maxLoad: 25000, // kilograms
  currentLoad: 12000,
  isMoving: false,
  mode: 'idle',
  log(message) {
    const stamp = new Date().toLocaleTimeString();
    logEl.textContent = `[${stamp}] ${message}\n` + logEl.textContent;
  },
  assertSafe(action) {
    if (this.currentLoad > this.maxLoad) {
      this.log(`⚠️ Overload detected (${this.currentLoad} kg > ${this.maxLoad} kg). Abort ${action}.`);
      return false;
    }
    if (this.isMoving) {
      this.log(`⏸️ Transition: slowing before ${action} to avoid shock loading.`);
    }
    return true;
  },
  move(action, detail) {
    if (!this.assertSafe(action)) return;
    this.isMoving = true;
    this.mode = action;
    this.log(`▶️ ${detail}`);
  },
  stop(reason = 'Controls neutralized, brakes applied.') {
    if (!this.isMoving && this.mode === 'idle') return;
    this.isMoving = false;
    this.mode = 'idle';
    this.log(`⛔ ${reason}`);
  },
};

function renderChecklist() {
  precheckEl.innerHTML = '';
  precheckItems.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    precheckEl.appendChild(li);
  });
}

function runChecklist() {
  crane.stop('Checklist run: controls confirmed neutral.');
  precheckItems.forEach((item, idx) => {
    setTimeout(() => crane.log(`✅ ${idx + 1}. ${item}`), idx * 350);
  });
  setTimeout(() => crane.log('📟 Status: cranes energized, systems ready for hoist.'), precheckItems.length * 350);
}

function bindButtons() {
  document.querySelectorAll('[data-action]').forEach((button) => {
    button.addEventListener('click', () => {
      const action = button.dataset.action;
      switch (action) {
        case 'hoist':
          crane.move('hoist', 'Hoisting with smooth, metered speed. Monitor boom deflection and load swing.');
          break;
        case 'lower':
          crane.move('lower', 'Lowering on the brake; keep tagline tension and avoid pendulum motion.');
          break;
        case 'luff-in':
          crane.move('luff', 'Luffing in to reduce radius; mind counterweight clearance.');
          break;
        case 'luff-out':
          crane.move('luff', 'Luffing out with radius increase; verify load chart margin.');
          break;
        case 'slew-port':
          crane.move('slew', 'Slewing to port with wind awareness and coordinated signalling.');
          break;
        case 'slew-starboard':
          crane.move('slew', 'Slewing to starboard; maintain constant slew speed through the swing.');
          break;
        default:
          crane.log('Unknown action.');
      }
    });
  });

  document.getElementById('emergency-stop').addEventListener('click', () => {
    crane.stop('Emergency stop activated. Hold position, secure load, and troubleshoot.');
  });

  document.getElementById('run-checklist').addEventListener('click', runChecklist);
  document.getElementById('reset-checklist').addEventListener('click', renderChecklist);

  document.getElementById('simulate-hoist').addEventListener('click', simulateHoistCycle);
  document.getElementById('simulate-transfer').addEventListener('click', simulateTransfer);
}

function simulateHoistCycle() {
  if (!crane.assertSafe('hoist cycle')) return;
  crane.log('📈 Hoist cycle start: warming hydraulic oil to 40–50°C and testing brakes.');
  crane.move('hoist', 'Hoisting at 80% rated speed with metered acceleration.');
  setTimeout(() => crane.move('slew', 'Slewing gently to align with hatch coaming.'), 600);
  setTimeout(() => crane.move('luff', 'Feathering luff out 1 m to clear coaming.'), 1200);
  setTimeout(() => crane.stop('Cycle complete: hook landed, brakes tested, controls neutral.'), 1800);
}

function simulateTransfer() {
  if (!crane.assertSafe('cargo transfer')) return;
  crane.log('🚢 Transfer: confirming signaller, exclusion zone, and weather limits.');
  crane.move('hoist', 'Hoist clear of deck with steady speed; monitor sway and boom deflection.');
  setTimeout(() => crane.move('slew', 'Slew to receiving side; keep hook over load path, avoid snagging.'), 800);
  setTimeout(() => crane.move('luff', 'Luff out to landing radius, maintaining load within chart limits.'), 1600);
  setTimeout(() => crane.move('lower', 'Lower under control; signaller spots landing and removes slack.'), 2400);
  setTimeout(() => crane.stop('Load landed, brakes applied, slew lock engaged for handover.'), 3200);
}

renderChecklist();
bindButtons();
crane.log('Ready: complete the checklist and operate with smooth, controlled motions.');
