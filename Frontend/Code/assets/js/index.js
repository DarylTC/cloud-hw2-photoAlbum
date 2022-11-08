var name = '';
var encoded = null;
var fileExt = null;
var SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const synth = window.speechSynthesis;
const recognition = new SpeechRecognition();
const icon = document.querySelector('i.fa.fa-microphone');


///// SEARCH TRIGGER //////
function searchFromVoice() {
  recognition.start();
  recognition.onresult = (event) => {
    const speechToText = event.results[0][0].transcript;
    console.log(speechToText);
    document.getElementById("searchbar").value = speechToText;
    search();
  }
}

function search() {
  var searchTerm = document.getElementById("searchbar").value;
  var apigClient = apigClientFactory.newClient({ apiKey: "8ePoxxPLXh876fJlwUGSq8qk2x5oEWo08hTZ9Gqk" });
  

    var body = { };
    var params = {
      q : searchTerm,
      'x-api-key' : '8ePoxxPLXh876fJlwUGSq8qk2x5oEWo08hTZ9Gqk',
      'Content-Type':"application/json"};
    console.log(params);
    
    

    apigClient.searchGet(params, { } , { }).then(function(res){
        console.log("success");
        console.log(res);
        showImages(res.data)
      }).catch(function(result){
          console.log(result);
          console.log("NO RESULT");
      });

}


/////// SHOW IMAGES BY SEARCH //////

function showImages(res) {
  var newDiv = document.getElementById("images");
  if(typeof(newDiv) != 'undefined' && newDiv != null){
  while (newDiv.firstChild) {
    newDiv.removeChild(newDiv.firstChild);
  }
  }
  
  console.log(res);
  if (res.length == 0) {
    var newContent = document.createTextNode("No image to display");
    newDiv.appendChild(newContent);
  }
  else {
    results=res['photoPath']
    console.log(results);

    // var newDiv = document.getElementById("images");
    // for (var i = 0; i < results.length; i++) {
    //   console.log(results[i]);
    //   filename = results[i].substring(results[i].lastIndexOf('/')+1)
    //   var newimg = document.createElement("img");
    //   newimg.src = "https://b2-dc4676.s3.amazonaws.com/"+filename;
    //   newDiv.appendChild(newimg);
    // }

    for (var i = 0; i < results.length; i++) {
      console.log(results[i]);
      filename = results[i].substring(results[i].lastIndexOf('/')+1)
      var request = new XMLHttpRequest();
      request.open('GET', "https://b2-dc4676.s3.amazonaws.com/"+filename, true);
      request.responseType = 'blob';
      request.onload = function() {
			console.log('request response')
		  	console.log(request.response)
			console.log('this response')
			console.log(this.response)
			var newDiv = document.getElementById("images");
			var newimg = document.createElement("img");
			var classname = randomChoice(['big', 'vertical', 'horizontal', '']);
			if(classname){newimg.classList.add();}
			var reader = new FileReader();
			reader.onload =  function(e){
					  newimg.src = 'data:image/*;base64, ' + (e.target.result);  
			};
			reader.readAsText(this.response, 'base64');
			newDiv.appendChild(newimg);
	  }
      request.send();
    }
    
  }
}


function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}



///// UPLOAD IMAGES ///////
function getBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    // reader.onload = () => resolve(reader.result)
    reader.onload = () => {
      let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
      if (encoded.length % 4 > 0) {
        encoded += '='.repeat(4 - (encoded.length % 4));
      }
      resolve(encoded);
    };
    reader.onerror = (error) => reject(error);
  });
}

const realFileBtn = document.getElementById("realfile");

var customelabel
function uploadImage() {
  realFileBtn.click(); 
  
  
 
  console.log(customelabel);
}

function previewFile(input) {
  var file = document.getElementById('realfile').files[0];
  customelabel = prompt("Please enter custome label", "trees");
  console.log(customelabel);
  var file_data;
  var encoded_image = getBase64(file).then((data) => {
      console.log(data);
      var apigClient = apigClientFactory.newClient({ apiKey: "8ePoxxPLXh876fJlwUGSq8qk2x5oEWo08hTZ9Gqk" });

      var file_type = file.type + ';base64';
      //var file_type = file.type;
      
      console.log(file.type);

      var body = data;
      var params = {
          key: file.name,
          bucket: 'b2-dc4676',
          'Content-Type': file.type,
          'x-amz-meta-customLabels': customelabel,
          Accept: 'image/*',
      };
      var additionalParams = {};
      apigClient
      .uploadPut(params, body, additionalParams)
      .then(function (res) {
          if (res.status == 200) {
            //console.log(result);
            console.log('success OK');
            alert("Photo Uploaded Successfully");
          }else{
            alert("You are dOOmed");
          }
      });
  });
  
}