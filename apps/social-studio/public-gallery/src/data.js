const dayCount = 30;
const gridSlotCount = 3;
const storySlotCount = 5;

export const galleryDays = Array.from({ length: dayCount }, (_, dayIndex) => {
  const day = dayIndex + 1;
  return {
    day,
    date: null,
    gridPosts: Array.from({ length: gridSlotCount }, (_, slotIndex) => ({
      slot: slotIndex + 1,
      label: `Grid slot ${String(slotIndex + 1).padStart(2, "0")}`,
      image: "",
      time: null
    })),
    stories: Array.from({ length: storySlotCount }, (_, slotIndex) => ({
      slot: slotIndex + 1,
      label: ["Open", "Context", "Detail", "Response", "Close"][slotIndex],
      image: "",
      time: null
    }))
  };
});

export const publicGalleryMeta = {
  title: "Social display gallery",
  accountLabel: "Hair Solutions Co.",
  handle: "@hairsolutions.co",
  status: "Public visual assembly",
  dataBoundary: "Sanitized structural fixture",
  revision: "Public gallery shell v1"
};
