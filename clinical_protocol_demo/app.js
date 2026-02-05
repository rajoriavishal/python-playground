
let usdm = null;
let mapping = [];

async function loadFiles() {

    usdm = await fetch("Response-GET-Study-v5.0 (1).json").then(r => r.json());
    document.getElementById("leftTree").textContent =
        JSON.stringify(usdm, null, 2);

    document.getElementById("protocolId").value = usdm.study?.id || "";

    const excel = await fetch("USDM_ICH_M11_Schema_Mapping.xlsx")
        .then(r => r.arrayBuffer());

    const workbook = XLSX.read(excel);
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    mapping = XLSX.utils.sheet_to_json(sheet);
}

loadFiles();

function getValue(obj, path) {
    return path.split('.').reduce((o, k) => (o || {})[k], obj);
}

function setValue(obj, path, value) {
    const keys = path.split('.');
    let cur = obj;

    keys.forEach((k, i) => {
        if (i === keys.length - 1) cur[k] = value;
        else {
            if (!cur[k]) cur[k] = {};
            cur = cur[k];
        }
    });
}

function convert() {

    let output = {};

    mapping.forEach(row => {

        if (!row["USDM Path"] || !row["ICH M11 Path"]) return;

        const source = `${row["USDM Path"]}.${row["USDM Field"]}`;
        const target = `${row["ICH M11 Path"]}.${row["ICH M11 Field"]}`;

        const value = getValue(usdm, source);

        if (value !== undefined)
            setValue(output, target, value);
    });

    document.getElementById("rightTree").textContent =
        JSON.stringify(output, null, 2);
}
