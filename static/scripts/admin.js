
function editChange(){
    console.log("Selection changed");
    var selected = document.getElementById("ename");
    var player = selected.options[selected.selectedIndex].value;
    var roleselect = document.getElementById("erole");

    var attributedisplay = document.getElementById("attr");

    attributedisplay.value = player;

    var currentRole = "";

    // looking for roles in classes
    console.log(player);

    if (player.search("Tank") > 0){
        currentRole = "Tank";
    }
    else if (player.search("Healer") > 0){
        currentRole = "Healer";
    }
    else if (player.search("DPS") > 0){
        currentRole = "DPS";
    }
    else {
        console.log("No role set")
    }


    // Tank = 1, Healer = 2, DPS = 3
    // TODO combine these hellish if structures
    if (currentRole == "Tank") {
        roleselect.selectedIndex = 1;
        console.log("Tank");
    }
    else if (currentRole == "Healer") {
        roleselect.selectedIndex = 2;
        console.log("Healer");
    }
    else if (currentRole == "DPS") {
        roleselect.selectedIndex = 3;
        console.log("DPS");
    }
    else {
        roleselect.selectedIndex = 0;
        console.log("No role or problem with detection")
    }
    
}
