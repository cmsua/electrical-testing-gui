boards = {
    # Low Density
    'ld-full': {
        'name': 'Low Density Full',
        'search_key': '320XLF',
        'image': 'static/assembled_electrical/ld-full/board.png',
        'hgcrocs_location': 'static/assembled_electrical/ld-full/hgcrocs.png',
        'hgcrocs': 3,
        'board_config': 'configs/initLD-trophyV3.yaml'
    },
    'ld-five': {
        'name': 'Low Density Five',
        'search_key': '320XL5',
        'image': 'static/assembled_electrical/ld-five/board.png',
        'hgcrocs_location': 'static/assembled_electrical/ld-five/hgcrocs.png',
        'hgcrocs': 3
    },
    'ld-semi-left': {
        'name': 'Low Density Semi Left',
        'search_key': '320XLL',
        'image': 'static/assembled_electrical/ld-semi-left/board.png',
        'hgcrocs_location': 'static/assembled_electrical/ld-semi-left/hgcrocs.png',
        'hgcrocs': 2
    },
    'ld-semi-right': {
        'name': 'Low Density Semi Right',
        'search_key': '320XLR',
        'image': 'static/assembled_electrical/ld-semi-right/board.png',
        'hgcrocs_location': 'static/assembled_electrical/ld-semi-right/hgcrocs.png',
        'hgcrocs': 2
    },

    'ld-half-top': {
        'name': 'Low Density Half Top',
        'search_key': '320XLT',
        'image': 'static/assembled_electrical/ld-half-top/board.png',
        'hgcrocs_location': 'static/assembled_electrical/ld-half-bottom/hgcrocs.png',
        'hgcrocs': 2
    },
    'ld-half-bottom': {
        'name': 'Low Density Half Bottom',
        'search_key': '320XLB',
        'image': 'static/assembled_electrical/ld-half-bottom/board.png',
        'hgcrocs_location': 'static/assembled_electrical/ld-half-bottom/hgcrocs.png',
        'hgcrocs': 2
    },
    
    # High Density
    'hd-full': {
        'name': 'High Density Full',
        'search_key': '320XHF',
        'image': 'static/assembled_electrical/hd-full/board.jpg',
        'hgcrocs_location': 'static/assembled_electrical/hd-full/hgcrocs.png',
        'hgcrocs': 6
    },
    'hd-top': {
        'name': 'High Density Top',
        'search_key': '320XHT',
        'image': 'static/assembled_electrical/hd-top/board.png',
        'hgcrocs_location': 'static/assembled_electrical/hd-bottom/hgcrocs.png',
        'hgcrocs': 3
    },
    'hd-bottom': {
        'name': 'High Density Bottom',
        'search_key': '320XHB',
        'image': 'static/assembled_electrical/hd-bottom/board.png',
        'hgcrocs_location': 'static/assembled_electrical/hd-bottom/hgcrocs.png',
        'hgcrocs': 4
    },
    'hd-semi-minus-left': {
        'name': 'High Density Semi Minus Left',
        'search_key': '320XHL',
        'image': 'static/assembled_electrical/hd-semi-minus-left/board.png',
        'hgcrocs_location': 'static/assembled_electrical/hd-semi-minus-left/hgcrocs.png',
        'hgcrocs': 2
    },
    'hd-semi-minus-right': {
        'name': 'High Density Semi Minus Right',
        'search_key': '320XHR',
        'image': 'static/assembled_electrical/hd-semi-minus-right/board.png',
        'hgcrocs_location': 'static/assembled_electrical/hd-semi-minus-right/hgcrocs.png',
        'hgcrocs': 2
    },

    # Invalid Board

    'default': {
        'name': 'Invalid Board',
        'search_key': 'invalid',
        'image': 'static/assembled_electrical/l3_loopback.jpg'
    }
}