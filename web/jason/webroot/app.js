const $ = document.getElementById.bind(document);

const types = {
    'audio': 'Audio',
    'images': 'Image',
    'yaml-json': 'YamlJson'
};
function submit(type) {
    const files = $(`${type}-file`).files;
    if (files.length === 0) {
        alert('Please select a file');
        return;
    }

    const inFormat = $(`${type}-from`).value;
    const outFormat = $(`${type}-to`).value;
    const reader = new FileReader();
    reader.onload = () => {
        const dataStart = reader.result.indexOf('base64,')+7;
        const req = {
            mode: `.convert.${types[type]}`,
            inFormat,
            inData: reader.result.substring(dataStart),
            outFormat
        };

        var ok;
        fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            redirect: 'follow',
            body: JSON.stringify(req)
        })
        .then(res => {
            if (res.status == 413) {
                throw 'File too large';
            }

            ok = res.ok;
            return res.json();
        })
        .then(res => {
            if (!ok) {
                var error = '';
                if (res.type == 'CommandException') {
                    error += `Are you sure the input was a ${inFormat}?\n`;
                }
                error += `${res.type}: ${res.message}`;
                alert(error);
                return;
            }

            $('result').src = `data:${res.mimeType};base64,${res.data}`;
        })
        .catch(e => alert(`Error: ${e}`));
    };
    reader.readAsDataURL(files[0]);
}

function addListeners(types) {
    types.forEach(t => $(`${t}-form`).addEventListener('submit', e => {
        e.preventDefault();
        submit(t);
    }));
}

window.onload = () => addListeners(['images', 'audio', 'yaml-json']);