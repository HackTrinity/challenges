function checker(id, i, l) {
    if(c(id, i, l)) {
        alert('Correct!');
    } else {
        alert('Incorrect.');
    }
}

function c(id, i, l) {
    // debugger;

    let answer = document.getElementById(`answer${id}`).value;

    if(answer.length !== l) {
        return false;
    }

    for(i_a=0; i_a<l; i_a++) {
        let char = answer[i_a];
        let blk = blks[i];
        
        if (!blk || (enc(char) !== get_blk(i))) {
            return false;
        }
        i++;
    }

    return true;
}

function enc(a) {
    return md5(md5(`${a}${salt}`));
}

function get_blk(i) {
    return md5(blks[i]);
}