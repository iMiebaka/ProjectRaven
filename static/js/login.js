// Mobile login and sign up form scripts
let signupBtn = document.getElementById("signupBtn");
signupBtn.addEventListener("click", signup);
let loginSwapBtn = document.getElementById("loginSwapBtn");
loginSwapBtn.addEventListener("click", login);
function signup(e) {
  let loginSection = document.getElementById("loginSection");
  loginSection.classList.add("d-none");

  let signupSection = document.getElementById("signupSection");
  signupSection.classList.remove("d-none");
  signupSection.classList.add("slide");
  e.preventDefault();
}
function login(e) {
  let signupSection = document.getElementById("signupSection");
  signupSection.classList.add("d-none");

  let loginSection = document.getElementById("loginSection");
  loginSection.classList.remove("d-none");
  loginSection.classList.add("slide");
  e.preventDefault();
}
// mobile login and sign up scripts end
$(function () {
  console.log("done");
  $(".sign-in-btn").click(function () {
    $(".w40").addClass("active");
    $(".sign-in-btn").addClass("active");
    $(".sign-up-btn").removeClass("active");
    $(".signInBox").removeClass("active");
    $(".signOutBox").addClass("active");
    $(".w40").removeClass("shift-left");
    $(".w60").removeClass("shift-right");
    $(".w60").addClass("active");
    $(".new-account-section").addClass("active");
    $(".sign-in-section").addClass("active");
  });
});
$(function () {
  console.log("done");
  $(".sign-up-btn").click(function () {
    $(".sign-in-btn").removeClass("active");
    $(".sign-up-btn").addClass("active");
    $(".w40").removeClass("active");
    $(".w40").addClass("shift-left");
    $(".signInBox").addClass("active");
    $(".signOutBox").removeClass("active");
    $(".w60").removeClass("active");
    $(".w60").addClass("shift-right");
    $(".new-account-section").removeClass("active");
    $(".sign-in-section").removeClass("active");
  });
});
