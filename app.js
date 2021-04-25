require('@tensorflow/tfjs-node')
const faceapi = require("@vladmandic/face-api")  
const canvas = require("canvas")  
const fs = require("fs")  
const path = require("path")
const NodeWebcam = require( "node-webcam" );

var five = require("johnny-five");
var board = new five.Board();

var emotion = 'neutral';

board.on("ready", function() {
  var red = new five.Pin(40);
  var green = new five.Pin(42);
  var blue = new five.Pin(44);
  button = new five.Button(30);

  // "up" the button is released
  button.on("up", function() {
    touch(emotion);
  });
  
  var state = 0x00;

  this.loop(200, function() {
    switch(emotion){
        case 'happy':
            red.write(0x00);
            green.write(0x00);
            blue.write(0x01);
        break;

        case 'sad':
            red.write(0x01);
            green.write(0x01);
            blue.write(0x00);
        break;

        case 'neutral':
            red.write(0x00);
            green.write(0x00);
            blue.write(0x00);
        break;   
    }
  });
});

var opts = {
    width: 1280,
    height: 720,
    quality: 100,
    frames: 60,
    delay: 0,
    saveShots: true,
    output: "jpeg",
    device: false,
    callbackReturn: "base64",
    verbose: false
};



var Webcam = NodeWebcam.create( opts );



// mokey pathing the faceapi canvas
const { Canvas, Image, ImageData } = canvas  
faceapi.env.monkeyPatch({ Canvas, Image, ImageData })

const faceDetectionNet = faceapi.nets.ssdMobilenetv1

// SsdMobilenetv1Options
const minConfidence = 0.5

// TinyFaceDetectorOptions
const inputSize = 408  
const scoreThreshold = 0.5

// MtcnnOptions
const minFaceSize = 50  
const scaleFactor = 0.8

function getFaceDetectorOptions(net) {  
    return net === faceapi.nets.ssdMobilenetv1
        ? new faceapi.SsdMobilenetv1Options({ minConfidence })
        : (net === faceapi.nets.tinyFaceDetector
            ? new faceapi.TinyFaceDetectorOptions({ inputSize, scoreThreshold })
            : new faceapi.MtcnnOptions({ minFaceSize, scaleFactor })
        )
}

const faceDetectionOptions = getFaceDetectorOptions(faceDetectionNet)

const emotionCutoff=0.3;
// simple utils to save files
const baseDir = path.resolve(__dirname, './out')  
function saveFile(fileName, buf) {  
    if (!fs.existsSync(baseDir)) {
        fs.mkdirSync(baseDir)
    }
    // this is ok for prototyping but using sync methods
    // is bad practice in NodeJS
    fs.writeFileSync(path.resolve(baseDir, fileName), buf)
  }

async function run2(){
   base="";
    await Webcam.capture( "face", async function( err, data ) {
        var img = new Image()
        base=data;
        img.src=base;

        const result = await faceapi.detectSingleFace(img).withFaceLandmarks().withFaceExpressions()
        
        const out = faceapi.createCanvasFromMedia(img)
        
        if(typeof result !== "undefined")
        {
            if(result.expressions.sad>emotionCutoff){
                emotion='sad';
            }else if(result.expressions.happy>emotionCutoff){
                emotion = 'happy';
            }else{
                emotion = 'neutral';
            }
        } 
        run2();
    } );
}

async function run() {
    await faceapi.nets.ssdMobilenetv1.loadFromDisk('weights')
    await faceapi.nets.tinyFaceDetector.loadFromDisk('weights')
    await faceapi.nets.faceLandmark68Net.loadFromDisk('weights')
    await faceapi.nets.faceExpressionNet.loadFromDisk('weights')
    run2();
}

run()


process.stdin.resume();
process.stdin.setEncoding('utf8');
process.stdin.on('data', function (chunk) {
    console.log(chunk);
    if(chunk.includes('skip')){
        touch('skip');       
    }
});

const time = new Date();

function touch(filename){
    try {
        fs.utimesSync(filename, time, time);
    } catch (err) {
        fs.closeSync(fs.openSync(filename, 'w'));
    }
    console.log('Wrote ' + filename);
}
