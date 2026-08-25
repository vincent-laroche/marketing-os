(() => {
  const search = document.querySelector("#search");
  const campaign = document.querySelector("#campaign-filter");
  const cards = [...document.querySelectorAll("[data-email-code][data-campaign]")];
  if (!(search instanceof HTMLInputElement) || !(campaign instanceof HTMLSelectElement)) return;

  const update = () => {
    const query = search.value.trim().toLowerCase();
    const selected = campaign.value;
    for (const card of cards) {
      const matchesQuery = !query || (card.getAttribute("data-email-code") || "").toLowerCase().includes(query);
      const matchesCampaign = !selected || card.getAttribute("data-campaign") === selected;
      card.hidden = !(matchesQuery && matchesCampaign);
    }
    for (const group of document.querySelectorAll("[data-campaign].campaign-group")) {
      group.hidden = !group.querySelector("[data-email-code]:not([hidden])");
    }
  };
  search.addEventListener("input", update);
  campaign.addEventListener("change", update);
})();
