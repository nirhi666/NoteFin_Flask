// --- NoteFin Web ---
// Drag, auto-save, delete confirmation, and icon toggle

// Muistilappujen piilotus/näyttö
function toggleNotesContainer() {
  const container = document.getElementById('notes');
  if (container) container.classList.toggle('hidden');
}

// Globaali z-index, jotta viimeksi siirretty on päällimmäisenä
let highestZ = 10;

// Lappujen drag & drop
function makeDraggable(el) {
  let offsetX = 0, offsetY = 0, isDragging = false;

  el.addEventListener('mousedown', e => {
    if (e.target.tagName === 'TEXTAREA') return;
    isDragging = true;
    el.classList.add('dragging');
    offsetX = e.clientX - el.offsetLeft;
    offsetY = e.clientY - el.offsetTop;
    el.style.zIndex = ++highestZ;
  });

  document.addEventListener('mousemove', e => {
    if (!isDragging) return;
    el.style.left = `${e.clientX - offsetX}px`;
    el.style.top = `${e.clientY - offsetY}px`;
  });

  const stopDrag = () => {
    if (isDragging) {
      isDragging = false;
      el.classList.remove('dragging');
    }
  };

  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('mouseleave', stopDrag);
}

// Kuvakkeen drag & drop
function makeIconDraggable(el) {
  let offsetX = 0, offsetY = 0, isDragging = false;

  el.addEventListener('mousedown', e => {
    isDragging = true;
    offsetX = e.clientX - el.offsetLeft;
    offsetY = e.clientY - el.offsetTop;
    el.style.transition = "none";
    el.style.zIndex = 9999;
  });

  document.addEventListener('mousemove', e => {
    if (!isDragging) return;
    el.style.left = (e.clientX - offsetX) + 'px';
    el.style.top = (e.clientY - offsetY) + 'px';
  });

  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      el.style.transition = "transform 0.1s ease, box-shadow 0.1s ease";
      el.style.zIndex = 100;
    }
  });
}

// Poiston varmistus
function confirmClear(noteId, isLocked) {
  if (isLocked) {
    alert("Lappu on lukittu, vapauta ennen poistamista.");
    return;
  }
  if (confirm("Haluatko varmasti tyhjentää tämän lapun?")) {
    window.location.href = "/clear/" + noteId;
  }
}

// DOM valmis
document.addEventListener("DOMContentLoaded", () => {
  // Lappujen drag
  document.querySelectorAll('.note').forEach(makeDraggable);

  // Automaattinen tallennus (Enter + blur)
  document.querySelectorAll('.note textarea').forEach(area => {
    area.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        area.form.submit();
      }
    });
    area.addEventListener('blur', () => area.form.submit());
  });

  // Poiston klikkaukset
  document.querySelectorAll('.clear-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const noteId = link.dataset.noteId;
      const isLocked = link.dataset.locked === 'true';
      confirmClear(noteId, isLocked);
    });
  });

  // Kuvakkeen drag
  const icon = document.getElementById('note-icon');
  if (icon) makeIconDraggable(icon);
});
// --- AJAX tallennus ilman sivun päivitystä ---
document.querySelectorAll('.note textarea').forEach(area => {
  area.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const form = area.form;
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form)
      }).then(res => res.json())
        .then(data => console.log("Tallennettu:", data))
        .catch(err => console.error(err));
    }
  });
});
