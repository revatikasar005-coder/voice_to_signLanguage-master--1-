const express = require("express");

const { spawn } = require('child_process');
const { Console } = require("console");
const app = express();
const path = require('path');
let ejs = require('ejs');
const fs = require("fs");

// express 4.16+ has built-in body parsing, and you must set "extended"
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.set('view engine', 'ejs');

const port = 3000
let inputLine = ""
let done = false
let dataString = ""
let requiredData = ""
var python = null
//static images file
app.use(express.static('public'));
app.use('/img', express.static('images'));

//Home page s2t.html
app.get("/", function (req, res) {
  inputLine = ""
  done = false
  dataString = ""
  requiredData = ""
  if (python != null)
    python.kill('SIGINT');
  res.sendFile(path.join(__dirname + "/s2t.html"));
});
//Final speach file done.html
app.post("/speach", function (req, res) {
  inputLine = (req.body.textbox || "").trim();
  if (!inputLine) {
    return res.render('result', { done: false, islSyntax: '', normalSyntax: '', error: 'Please enter text.' });
  }

  if (done == false) {
    isItDoneYet().then((msg) => {
      console.log(msg)
      console.log(inputLine)
      if (done)
        res.render('result', { done: done, islSyntax: requiredData, normalSyntax: inputLine })
      console.log("data->\n" + dataString)
      let startIndex = dataString.indexOf("ISL:{")
      let endIndex = dataString.indexOf("}")
      requiredData = dataString.substring(startIndex + 5, endIndex);
      res.render('result', { done: done, islSyntax: requiredData, normalSyntax: inputLine })
      done = true;
    }).catch((err) => {
      console.log(err);
      res.render('result', { done: false, islSyntax: '', normalSyntax: inputLine, error: err.toString() });
    })
  }
  else{
    res.render('result', { done: done, islSyntax: requiredData, normalSyntax: inputLine })
  }
});
//done request video 
app.get("/video", function (req, res) {
  
  //res.sendFile('/data/samples/output/clipg.mp4', { root: __dirname });  
  const range = req.headers.range;
  if (!range) {
    res.status(400).send("Requires Range header");
  }

  // get video stats (about 61MB)
  const videoPath = path.resolve(__dirname + "/data/samples/output/clipg.mp4");
  const videoSize = fs.statSync(videoPath).size;

  // Parse Range
  // Example: "bytes=32324-"
  const CHUNK_SIZE = 10 ** 6; // 1MB
  const start = Number(range.replace(/\D/g, ""));
  const end = Math.min(start + CHUNK_SIZE, videoSize - 1);

  // Create headers
  const contentLength = end - start + 1;
  const headers = {
    "Content-Range": `bytes ${start}-${end}/${videoSize}`,
    "Accept-Ranges": "bytes",
    "Content-Length": contentLength,
    "Content-Type": "video/mp4",
  };

  // create video read stream for this particular chunk
  var videoStream = fs.createReadStream(videoPath, { start, end });

  // HTTP Status 206 for Partial Content
  res.writeHead(206, headers);


  // Stream the video chunk to the client
  videoStream.pipe(res);
})

//this the python promise 
const isItDoneYet = () => new Promise((resolve, reject) => {
  // Use the project venv python if present.
  const pyCmd = process.platform === 'win32'
    ? path.join(__dirname, '.venv', 'Scripts', 'python.exe')
    : path.join(__dirname, '.venv', 'bin', 'python');

  const pythonCmd = require('fs').existsSync(pyCmd) ? pyCmd : 'python';

  python = spawn(pythonCmd, ['speech_recog.py', inputLine], { cwd: __dirname });

  let stderr = '';
  python.stdout.on('data', (data) => {
    dataString += data.toString();
  });
  python.stderr.on('data', (data) => {
    stderr += data.toString();
    console.error('python stderr:', data.toString());
  });
  python.on('error', (err) => {
    console.error('python spawn error:', err);
    reject(err);
  });
  python.on('close', (code) => {
    console.log(`child process close all stdio with code ${code}`);
    if (code === 0) {
      resolve('Here is the thing I built');
      return;
    }
    reject(new Error(`python process failed code=${code} stderr=${stderr}`));
  });
});

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
