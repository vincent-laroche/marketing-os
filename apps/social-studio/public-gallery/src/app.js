import { galleryDays, publicGalleryMeta } from "./data.js";

const dailyRows = document.querySelector("#dailyRows");
const dayJump = document.querySelector("#dayJump");
const feedGrid = document.querySelector("#feedGrid");

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function formatDate(date) {
  if (!date) return "Date not set";
  const parsed = new Date(`${date}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(parsed);
}

function formatTime(time) {
  return time || "Time unset";
}

function safeImageSource(source) {
  if (!source) return "";
  if (source.startsWith("/assets/") || source.startsWith("https://assets.hairsolutions.co/")) return source;
  return "";
}

function appendImageOrSlot(container, image, slotLabel, ratioLabel) {
  const source = safeImageSource(image);
  if (source) {
    const img = document.createElement("img");
    img.src = source;
    img.alt = `${slotLabel} visual`;
    img.loading = "lazy";
    container.append(img);
    return;
  }

  const slot = el("div", "photoSlot");
  slot.append(el("strong", "", "Place approved photo"));
  slot.append(el("small", "", ratioLabel));
  container.append(slot);
}

function renderDayJump() {
  galleryDays.forEach(({ day }) => {
    const link = el("a", "dayJumpLink", String(day).padStart(2, "0"));
    link.href = `#day-${day}`;
    link.setAttribute("aria-label", `Jump to day ${day}`);
    dayJump.append(link);
  });
}

function renderGridPost(post) {
  const card = el("article", "gridPostCard");
  const media = el("div", "gridPostMedia");
  appendImageOrSlot(media, post.image, post.label, "1:1 square");
  media.append(el("span", "slotIndex", String(post.slot).padStart(2, "0")));
  card.append(media);

  const meta = el("div", "gridPostMeta");
  meta.append(el("strong", "", post.label));
  meta.append(el("span", "", formatTime(post.time)));
  card.append(meta);
  return card;
}

function renderStoryFrame(frame) {
  const card = el("article", "storyCard");
  const media = el("div", "storyMedia");
  appendImageOrSlot(media, frame.image, `Story ${frame.label}`, "9:16 portrait");
  media.append(el("span", "slotIndex", String(frame.slot).padStart(2, "0")));
  card.append(media);

  const meta = el("div", "storyMeta");
  meta.append(el("strong", "", frame.label));
  meta.append(el("span", "", formatTime(frame.time)));
  card.append(meta);
  return card;
}

function renderDay(dayRecord) {
  const row = el("article", "dayRow");
  row.id = `day-${dayRecord.day}`;

  const rail = el("header", "dayRail");
  const dayLabel = el("span", "eyebrow", "Launch day");
  const dayNumber = el("strong", "dayNumber", String(dayRecord.day).padStart(2, "0"));
  const schedule = el("div", "daySchedule");
  schedule.append(el("time", "", formatDate(dayRecord.date)));
  schedule.append(el("span", "", "Publish time unset"));
  const count = el("span", "dayCount", "3 grid posts · 5 Stories");
  const status = el("span", "statusPill", "Public visual shell");
  rail.append(dayLabel, dayNumber, schedule, count, status);
  row.append(rail);

  const body = el("div", "dayBody");
  const gridSection = el("section", "daySection");
  const gridHeader = el("div", "sectionHeader");
  gridHeader.append(el("div", "", ""));
  gridHeader.firstChild.append(el("span", "eyebrow", "Instagram grid"));
  gridHeader.firstChild.append(el("h3", "", "Three square slots"));
  gridHeader.append(el("span", "sectionNote", "Place approved photos"));
  gridSection.append(gridHeader);
  const grid = el("div", "gridPostList");
  dayRecord.gridPosts.forEach((post) => grid.append(renderGridPost(post)));
  gridSection.append(grid);

  const storySection = el("section", "daySection storiesSection");
  const storyHeader = el("div", "sectionHeader");
  storyHeader.append(el("div", "", ""));
  storyHeader.firstChild.append(el("span", "eyebrow", "Stories alongside"));
  storyHeader.firstChild.append(el("h3", "", "Five portrait slots"));
  storyHeader.append(el("span", "sectionNote", "9:16 story frame"));
  storySection.append(storyHeader);
  const storyTrack = el("div", "storyList");
  dayRecord.stories.forEach((frame) => storyTrack.append(renderStoryFrame(frame)));
  storySection.append(storyTrack);

  body.append(gridSection, storySection);
  row.append(body);
  return row;
}

function renderFeedAssembly() {
  const posts = galleryDays.flatMap((day) => day.gridPosts.map((post) => ({ ...post, day: day.day }))).slice(0, 9);
  posts.forEach((post, index) => {
    const tile = el("div", "feedTile");
    appendImageOrSlot(tile, post.image, `Feed slot ${index + 1}`, "1:1 square");
    tile.append(el("span", "tileIndex", String(index + 1).padStart(2, "0")));
    tile.append(el("strong", "", `Day ${post.day} / slot ${post.slot}`));
    feedGrid.append(tile);
  });
}

function render() {
  document.querySelectorAll("[data-gallery-account]").forEach((node) => { node.textContent = publicGalleryMeta.accountLabel; });
  document.querySelectorAll("[data-gallery-handle]").forEach((node) => { node.textContent = publicGalleryMeta.handle; });
  renderDayJump();
  galleryDays.forEach((day) => dailyRows.append(renderDay(day)));
  renderFeedAssembly();
}

render();
