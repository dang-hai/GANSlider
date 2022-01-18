export function check_valid(data, edits) {
    // console.log(data, edits)
    if (!data) { return false }
    const content = data.content;
    let resp_edits = content.interaction.edits;


    const edits_equal = resp_edits.map((elem, idx) => parseFloat(edits[idx].value) == parseFloat(elem.value))

    const arr_equal = edits_equal.every(elem => elem)

    return content.image_data.length > 0 && arr_equal
}
