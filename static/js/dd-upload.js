var ddup = {
    // (A) ON PAGE LOAD
    hzone: null, // HTML upload zone
    hstat: null, // HTML upload status
    hform: null, // HTML upload form
    init : function () {
      // (A1) GET HTML ELEMENTS
      ddup.hzone = document.getElementById("upzone");
      ddup.hstat = document.getElementById("upstat");
      ddup.hform = document.getElementById("upform");
      
      // (A2) DRAG-DROP SUPPORTED
      if (window.File && window.FileReader && window.FileList && window.Blob) {
        // HIGHLIGHT DROPZONE ON FILE HOVER
        ddup.hzone.addEventListener("dragenter", function (e) {
          e.preventDefault();
          e.stopPropagation();
          ddup.hzone.classList.add('highlight');
        });
        ddup.hzone.addEventListener("dragleave", function (e) {
          e.preventDefault();
          e.stopPropagation();
          ddup.hzone.classList.remove('highlight');
        });
        
        // DROP TO UPLOAD FILE
        ddup.hzone.addEventListener("dragover", function (e) {
          e.preventDefault();
          e.stopPropagation();
        });
        ddup.hzone.addEventListener("drop", function (e) {
          e.preventDefault();
          e.stopPropagation();
          ddup.hzone.classList.remove('highlight');
          ddup.queue(e.dataTransfer.files);
        });
      }
  
      // (A3) DRAG-DROP UPLOAD NOT SUPPORTED
      else {
        ddup.hzone.style.display = "none";
        ddup.hform.style.display = "block";
      }
    }
  }
  window.addEventListener("DOMContentLoaded", ddup.init);