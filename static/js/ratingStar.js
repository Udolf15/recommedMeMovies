
// check if there is a rating stars div on the page
if(document.querySelector(".starIcon1") != undefined){

    // initialize the rating stars list as a global variable to reuse it later
    let stars = [];

    // init the stars query selectors
    function starQueryInit(){
        // create the querySelector of each 5 stars and push it to the stars list
        for(let i=1; i <= 5; i++){
            stars.push(document.querySelector(".starIcon"+i));
        }
    }

    // remove the clickedStar class on every stars
    function removeClickedStar(){
        for(let i = 0; i < stars.length; i++){
            stars[i].classList.remove("clickedStar");
        }
    }

    // add the clickedStar function when clicked and check his radio button
    function addClickedStar(numStar){
        // clickedStar function when clicked
        for(let i = 0; i < numStar; i++){
            stars[i].classList.add("clickedStar");
        }
        // check his radio button
        document.querySelector("input[type=radio].star"+numStar).checked = true;
        let checkedValue = document.querySelector('input[name="comment[rating]"]:checked').value;
        // console.log(checkedValue);
        
    }

    // translate hover effect
    function translateHover(numStar, translateY){
        for(let i = 0; i < numStar; i++){
            stars[i].style.transform = translateY;
        }
    }

    function createRatingEventListeners(){
        // create the translateY up and down values
        let translateLst = ["translateY(-5px)", "translateY(0px)"];
        // iterate over the stars and add event listeners
        for(let i = 0; i < stars.length; i++){
            // set the number of star value
            let numStar = i+1;

            // hover effect translateY up and down
            // add the up translateY hover effect
            stars[i].addEventListener("mouseover", ()=>{
                translateHover(numStar, translateLst[0]);
            });
            // add the up translateY hover effect
            stars[i].addEventListener("mouseout", ()=>{
                translateHover(numStar, translateLst[1]);
            });

            // click event listener (change color and check the radio button)
            stars[i].addEventListener("click", ()=> {
                // remove all the clickedStar
                removeClickedStar();
                // add clickedStar and check his radio button
                addClickedStar(numStar);
            });
        }
    }

    // init the stars query selectors
    starQueryInit();
    // create the events listeners
    createRatingEventListeners();
}