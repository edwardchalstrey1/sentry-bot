function testFunc() {
    xpos = document.getElementById("xpos").value
    ypos = document.getElementById("ypos").value
    var params = new URLSearchParams();
    params.append('xPos', xpos);
    params.append('yPos', ypos);
    var url = '/set_desired_coords?' + params.toString();
    fetch(url)
        .then(response => response.text())
        .then(text => console.log(text))
}

function fire() {
    console.log('Fire on target!')
    xpos = document.getElementById("xpos").value
    ypos = document.getElementById("ypos").value
    var params = new URLSearchParams();
    params.append('xPos', xpos);
    params.append('yPos', ypos);
    params.append('shouldFire', true)
    var url = '/set_desired_coords?' + params.toString();
    fetch(url)
        .then(response => response.text())
        .then(text => console.log(text))
}

function hideDiv() {
    const elementToHide = document.querySelector('.top');
    if (elementToHide.style.display == 'block') {
        elementToHide.style.display = 'none';
    } else {
        elementToHide.style.display = 'block';
    }

}

function toggle_mode() {
    console.log("Toggle mode")
    var url = '/ajax-data?toggleAutoAiming=1';
    fetch(url)
        .then(response => response.text())
        .then(text => console.log(text))

}


var widescreen = true;
function enlarge() {
    const selector = '.videocontainer img';
    const width = widescreen ? '150vmin' : '70vmin';
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
        element.style.width = width;
    });
    widescreen = !widescreen;
}
