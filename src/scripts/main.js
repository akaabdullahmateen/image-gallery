async function populateSlides() {
  // Test if browser supports HTML5 template element by checking for the presence of template element's content attribute

  if (!("content" in document.createElement("template"))) {
    const errorMessage = document.createElement("p");
    errorMessage.textContent = "Your browser does not support HTML5 template elements!";
    document.querySelector(".root").removeChild(document.querySelector(".gallery"));
    document.querySelector(".root").appendChild(errorMessage);

    return;
  }

  const gallery = document.querySelector(".gallery");
  const slideTemplate = document.getElementById("slide-template");

  const requestURL = "src/assets/data/talent.json";
  const request = new Request(requestURL);
  const response = await fetch(request);
  const talents = await response.json();

  for (const talent of talents) {
    const slideClone = slideTemplate.content.firstElementChild.cloneNode(true);
    slideClone.querySelector(".slide--picture").src = talent["profile_image"];
    slideClone.querySelector(".slide--name").textContent = talent["talent_name"];
    slideClone.querySelector(".slide--description").textContent = talent["talent_profession"];
    initializeToolbar(slideClone);
    gallery.appendChild(slideClone);
  }

  initializeCarousel();
}

function initializeToolbar(slide) {
  const tools = slide.querySelectorAll(".slide--toolbar button");
  const scale = slide.querySelector(".slide--scale");
  const maxValues = { blur: 20, brightness: 200, contrast: 200, grayscale: 100, huerotate: 360 };
  const stepValues = { blur: 1, brightness: 10, contrast: 10, grayscale: 5, huerotate: 18 };
  const defaultValues = { blur: 0, brightness: 100, contrast: 100, grayscale: 0, huerotate: 0 };
  const filters = { blur: "blur", brightness: "brightness", contrast: "contrast", grayscale: "grayscale", huerotate: "hue-rotate" };
  const units = { blur: "px", brightness: "%", contrast: "%", grayscale: "%", huerotate: "deg" };

  scale.addEventListener("input", () => {
    const activeTool = slide.querySelector(".active");
    const activeClass = activeTool.classList[0];
    const slidePicture = slide.querySelector(".slide--picture");

    slidePicture.style.filter = `${filters[activeClass]}(${scale.value}${units[activeClass]})`;
  });

  for (const tool of tools) {
    tool.addEventListener("click", (e) => {
      for (const anyTool of tools) {
        anyTool.classList.remove("active");
      }

      const currentTool = e.currentTarget;
      currentTool.classList.add("active");

      const toolClass = currentTool.classList[0];

      scale.setAttribute("max", maxValues[toolClass]);
      scale.setAttribute("step", stepValues[toolClass]);
      scale.value = defaultValues[toolClass];

      e.stopPropagation();
    });
  }

  tools[0].classList.add("active");
  scale.value = defaultValues["blur"];
}

function activateCarousel(index) {
  const slides = document.querySelectorAll(".slide");
  const slide = slides[index];

  if (slide.classList.contains("active")) {
    return;
  }

  slide.classList = "slide active";

  if (slides[index - 2] != undefined) {
    slides[index - 2].classList = "slide lhidden";
  }
  if (slides[index - 1] != undefined) {
    slides[index - 1].classList = "slide lqueue";
  }
  if (slides[index + 1] != undefined) {
    slides[index + 1].classList = "slide rqueue";
  }
  if (slides[index + 2] != undefined) {
    slides[index + 2].classList = "slide rhidden";
  }
}

function initializeCarousel() {
  const slides = document.querySelectorAll(".slide");

  for (let index = 0; index < slides.length; index++) {
    const slide = slides[index];
    slide.classList.add("rhidden");
    slide.addEventListener("click", () => {
      activateCarousel(index);
    });
  }

  slides[0].classList = "slide active";
  slides[1].classList = "slide rqueue";
}

populateSlides();
