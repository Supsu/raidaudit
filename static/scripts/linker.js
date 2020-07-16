function createlinks() {

    console.log("Link creation started");

    var table = document.getElementById("rostertable");

    // TODO iterate over table, then get innerHTML from cells[1],
    // a elements from cells[0] and generate href's

    // https://www.warcraftlogs.com/character/<region>/<realm>/<name>
    // https://raider.io/characters/<region>/<realm>/<name>
    // https://worldofwarcraft.com/<locale>/character/<region>/<realm>/<name>

    data  = table.getAttribute("data-links");
    console.log(data)

    linkdata = JSON.parse(data);

    var region = linkdata["region"];
    var realm = linkdata["realm"];
    var locale = linkdata["locale"];

    var slash = "/";
    var wclroot = "http://warcraftlogs.com/character/";
    var wowroot = "https://www.worldofwarcraft.com/";
    var rioroot = "https://raider.io/characters/";

    

    var idx;
    console.log("Table rows");
    console.log(table.rows);

    console.log("Starting loop");

    for ( idx = 1; idx < table.rows.length; idx++ ) {
        var row = table.rows[idx];
        var name = row.cells[1].children[0].innerHTML.trim();

        console.log(name);

        links = row.cells[0].children[0].getElementsByTagName("A");

        var wowurl = wowroot.concat(locale, slash, "character", slash, region, slash, realm, slash, name);
        var wclurl = wclroot.concat(region, slash, realm, slash, name);
        var riourl = rioroot.concat(region, slash, realm, slash, name);

        links[0].setAttribute("href", wowurl);
        links[1].setAttribute("href", wclurl);
        links[2].setAttribute("href", riourl);

    }

}

window.onload = createlinks;