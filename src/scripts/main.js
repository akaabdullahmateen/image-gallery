async function populateSlides() {
  // Test if browser supports HTML5 template element by checking for the presence of template element's content attribute

  if (!("content" in document.createElement("template"))) {
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
    gallery.appendChild(slideClone);
  }

  initializeCarousel();
}

function activateCarousel(index) {
  const slides = document.querySelectorAll(".slide");
  const slide = slides[index];

  if (slide.classList.contains("active")) {
    return;
  }

  if (slide.classList.contains("rqueue")) {
    slide.classList = "slide active";
  }

  if (slide.classList.contains("lqueue")) {
    slide.classList = "slide active";
  }

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
