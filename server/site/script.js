let temp = document.getElementById("temp");
let humid = document.getElementById("humid");
let image0 = document.getElementById("image0");
let image1 = document.getElementById("image1");
let images_input = document.getElementById("images_input")
let images_output = document.getElementById("images_output")
let textbox = document.getElementById("textbox");
let graph_input = document.getElementById("graph_input")
let graph_button = document.getElementById("graph_button");
let images_button = document.getElementById("images_button");
let graph_output = document.getElementById("graph_output")
let numbox = document.getElementById("numbox")

window.onload = function() {
    fetch('/api/env')
        .then(resp => resp.text())
        .then(text => {env.textContent = text})    
}

function get_image() {
    images_input.hidden = true;
    images_output.hidden = false;
    pass = (textbox.value === '' ? 'emptyyyy' : textbox.value); 
    image0.src = '/api/image/' + pass + '/0';
    image1.src = '/api/image/' + pass + '/1';
}

function get_graph() {
    graph_input.hidden = true;
    graph_output.hidden = false;
    const selection = document.querySelector('input[name="graph_selection"]:checked').value;
    const hours = numbox.value
    graph_output.src = '/api/env/graph/' + selection + '/' + (hours + (hours.includes(".") ? "" : ".0"));    
}
