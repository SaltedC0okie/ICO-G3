function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

var percent = 0;

async function say_cenas() {
    while (false) { // while (true) {
        await sleep(500);
        check_progess();
        update_progress();
    }
}

$('.content').on('submit', function () {
    console.log("Button clicked");
    say_cenas();
    return true;
});

function check_progess() {
    $.ajax({
        type: "GET",
        url: "progress_bar",
        success: function(result) {
             if(result.error == 0) {
                percent = result.percent;
             }
        },
        error: function(result) {
            console.log('error');
        }
    });
}

function update_progress() {
    console.log("Progress at " + percent + "%");
    const myProgressBar = document.querySelector(".progress");
    updateProgressBar(myProgressBar, percent);
}

function updateProgressBar(progressBar, value) {
  value = Math.round(value * 100) / 100;
  progressBar.querySelector(".progress__fill").style.width = `${value}%`;
  progressBar.querySelector(".progress__text").textContent = `${value}%`;
}

