const state = {
  events: [],
  currentIndex: 0,
  editingId: null,
};

const elements = {
  count: document.querySelector("#entry-count"),
  position: document.querySelector("#current-position"),
  list: document.querySelector("#timeline-list"),
  emptyState: document.querySelector("#empty-state"),
  detail: document.querySelector("#entry-detail"),
  detailEmpty: document.querySelector("#detail-empty"),
  previous: document.querySelector("#previous-button"),
  next: document.querySelector("#next-button"),
  edit: document.querySelector("#edit-button"),
  delete: document.querySelector("#delete-button"),
  formPanel: document.querySelector("#entry-form-panel"),
  form: document.querySelector("#entry-form"),
  formHeading: document.querySelector("#form-heading"),
  formError: document.querySelector("#form-error"),
  save: document.querySelector("#save-button"),
  toast: document.querySelector("#toast"),
};

let toastTimer;

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "The request could not be completed.");
  }
  return payload;
}

function formatDate(value, options = { dateStyle: "medium", timeStyle: "short" }) {
  return new Intl.DateTimeFormat(undefined, options).format(new Date(value));
}

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("is-error", isError);
  elements.toast.classList.add("is-visible");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => elements.toast.classList.remove("is-visible"), 3200);
}

function createTextElement(tag, className, text) {
  const element = document.createElement(tag);
  element.className = className;
  element.textContent = text;
  return element;
}

function render() {
  const event = state.events[state.currentIndex];
  elements.count.textContent = state.events.length;
  elements.position.textContent = event ? `${state.currentIndex + 1} / ${state.events.length}` : "—";
  elements.list.replaceChildren();
  elements.emptyState.hidden = state.events.length !== 0;
  elements.detail.hidden = !event;
  elements.detailEmpty.hidden = Boolean(event);
  elements.edit.disabled = !event;
  elements.delete.disabled = !event;
  elements.previous.disabled = !event || state.currentIndex === 0;
  elements.next.disabled = !event || state.currentIndex === state.events.length - 1;

  state.events.forEach((entry, index) => {
    const item = document.createElement("li");
    item.className = `timeline-item${index === state.currentIndex ? " is-current" : ""}`;
    item.tabIndex = 0;
    item.setAttribute("aria-current", index === state.currentIndex ? "step" : "false");
    item.setAttribute("aria-label", `${entry.title}, ${formatDate(entry.recorded_at)}`);
    item.addEventListener("click", () => selectEntry(index));
    item.addEventListener("keydown", (keyboardEvent) => {
      if (keyboardEvent.key === "Enter" || keyboardEvent.key === " ") {
        keyboardEvent.preventDefault();
        selectEntry(index);
      }
    });
    const node = document.createElement("span");
    node.className = "timeline-node";
    node.setAttribute("aria-hidden", "true");
    const copy = document.createElement("div");
    copy.className = "timeline-item-copy";
    copy.append(
      createTextElement("p", "timeline-item-title", entry.title),
      createTextElement("div", "timeline-item-meta", `${formatDate(entry.recorded_at)} · ${entry.location}`),
    );
    item.append(node, copy);
    elements.list.append(item);
  });

  if (event) {
    renderDetails(event);
  } else {
    elements.detail.replaceChildren();
  }
}

function renderDetails(event) {
  const content = document.createDocumentFragment();
  content.append(
    createTextElement("p", "entry-overline", `RECORD ${String(state.currentIndex + 1).padStart(2, "0")} · ${formatDate(event.recorded_at)}`),
    createTextElement("h3", "entry-title", event.title),
  );

  const meta = document.createElement("div");
  meta.className = "detail-meta-grid";
  [
    ["Location", event.location],
    ["Conservator", event.conservator],
  ].forEach(([label, value]) => {
    const field = document.createElement("div");
    field.append(
      createTextElement("span", "detail-meta-label", label),
      createTextElement("div", "detail-meta-value", value),
    );
    meta.append(field);
  });
  content.append(meta);
  content.append(
    createDetailSection("Treatment / observation", event.treatment),
    createDetailSection("Materials and equipment", event.materials || "No materials recorded."),
    createDetailSection("Notes", event.notes || "No additional notes."),
  );
  elements.detail.replaceChildren(content);
}

function createDetailSection(title, value) {
  const section = document.createElement("section");
  section.className = "detail-section";
  section.append(
    createTextElement("h3", "", title),
    createTextElement("p", "", value),
  );
  return section;
}

function selectEntry(index) {
  state.currentIndex = index;
  closeForm();
  render();
}

async function loadEvents(direction = "forward", selectedId = null) {
  const payload = await request(`/api/events?direction=${direction}`);
  state.events = payload.events;
  const selectedIndex = selectedId
    ? state.events.findIndex((event) => event.id === selectedId)
    : -1;
  state.currentIndex = selectedIndex >= 0
    ? selectedIndex
    : Math.min(state.currentIndex, state.events.length - 1);
  if (state.currentIndex < 0) state.currentIndex = 0;
  render();
}

function openForm(event = null) {
  state.editingId = event?.id ?? null;
  elements.form.reset();
  elements.formError.hidden = true;
  elements.formHeading.textContent = event ? "Edit treatment entry" : "Add treatment entry";
  elements.save.textContent = event ? "Save changes" : "Save entry";

  if (event) {
    Object.entries(event).forEach(([key, value]) => {
      const field = elements.form.elements.namedItem(key);
      if (field) field.value = key === "recorded_at" ? value.slice(0, 16) : value;
    });
  } else {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    elements.form.elements.namedItem("recorded_at").value = now.toISOString().slice(0, 16);
  }

  elements.formPanel.hidden = false;
  elements.formPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  elements.form.elements.namedItem("title").focus({ preventScroll: true });
}

function closeForm() {
  elements.formPanel.hidden = true;
  state.editingId = null;
}

async function saveEntry(formEvent) {
  formEvent.preventDefault();
  elements.formError.hidden = true;
  elements.save.disabled = true;
  const fields = Object.fromEntries(new FormData(elements.form).entries());

  try {
    let savedEventId;
    if (state.editingId) {
      const result = await request(`/api/events/${encodeURIComponent(state.editingId)}`, {
        method: "PUT",
        body: JSON.stringify(fields),
      });
      savedEventId = result.event.id;
      showToast("Treatment entry updated.");
    } else {
      const result = await request("/api/events", {
        method: "POST",
        body: JSON.stringify({ ...fields, index: state.events.length ? state.currentIndex + 1 : 0 }),
      });
      savedEventId = result.event.id;
      showToast("Treatment entry added to the timeline.");
    }
    closeForm();
    await loadEvents("forward", savedEventId);
  } catch (error) {
    elements.formError.textContent = error.message;
    elements.formError.hidden = false;
  } finally {
    elements.save.disabled = false;
  }
}

async function deleteCurrentEntry() {
  const event = state.events[state.currentIndex];
  if (!event || !window.confirm(`Delete "${event.title}" from the treatment record?`)) return;
  try {
    await request(`/api/events/${encodeURIComponent(event.id)}`, { method: "DELETE" });
    state.currentIndex = Math.max(0, state.currentIndex - 1);
    await loadEvents();
    showToast("Treatment entry deleted.");
  } catch (error) {
    showToast(error.message, true);
  }
}

document.querySelector("#new-entry-button").addEventListener("click", () => openForm());
document.querySelector("#empty-add-button").addEventListener("click", () => openForm());
document.querySelector("#close-form-button").addEventListener("click", closeForm);
document.querySelector("#cancel-form-button").addEventListener("click", closeForm);
elements.form.addEventListener("submit", saveEntry);
elements.previous.addEventListener("click", () => selectEntry(state.currentIndex - 1));
elements.next.addEventListener("click", () => selectEntry(state.currentIndex + 1));
elements.edit.addEventListener("click", () => openForm(state.events[state.currentIndex]));
elements.delete.addEventListener("click", deleteCurrentEntry);
document.querySelector("#footer-year").textContent = new Date().getFullYear();

loadEvents().catch((error) => {
  showToast(error.message, true);
  elements.emptyState.hidden = false;
  elements.emptyState.querySelector("h3").textContent = "Could not load the treatment record";
  elements.emptyState.querySelector("p").textContent = error.message;
});
