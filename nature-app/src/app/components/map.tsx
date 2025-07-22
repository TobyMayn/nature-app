"use client";
import { Map, View } from "ol";
import Modify from 'ol/interaction/Modify.js';
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import "ol/ol.css";
import { get as getProjection } from "ol/proj";
import { register } from 'ol/proj/proj4';
import { OSM } from "ol/source";
import VectorSource from "ol/source/Vector";
import proj4 from 'proj4';
import { useEffect } from "react";

function MapView() {
    // 1. Projection Definition (from previous setup, confirmed by capabilities)
    const projectionCode = 'EPSG:25832';
    const projectionDefinition = '+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs';
    proj4.defs(projectionCode, projectionDefinition);
    register(proj4);

    const proj = getProjection(projectionCode);

    // 2. Projection Extent (from <ows:BoundingBox> in GetCapabilities)
    const projectionExtent = [120000, 5900000, 1000000, 6500000];

    // 3. Tile Grid Origin (from <TopLeftCorner> in GetCapabilities)
    // Note: OpenLayers getTopLeft(extent) can be used if origin == top-left of extent.
    // However, the GetCapabilities explicitly states TopLeftCorner for the TileMatrixSet.
    const origin = [120000.000000, 6500000.000000]; // This is (minX, maxY)

    // 4. Resolutions (calculated from ScaleDenominator in GetCapabilities)
    // Using the formula: Resolution = ScaleDenominator / 90.71428571428571 (common for web maps)
    const resolutions = [
        64500.0,
        32250.0,
        16125.0,
        8062.5,
        4031.25,
        2015.625,
        1007.8125,
        503.90625,
        251.953125,
        125.9765625,
        62.98828125,
        31.494140625,
        15.7470703125,
        7.87353515625,
    ];

    // 5. Matrix IDs (from <ows:Identifier> under each <TileMatrix>)
    // These correspond to your zoom levels 0-13.
    const matrixIds = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'
    ];

    // 6. Tile Size (from <TileWidth> and <TileHeight> in GetCapabilities)
    // It's 256x256, which is OpenLayers default, but good to be explicit.
    const tileSize = 256;

    const source = new VectorSource();
    const vector = new VectorLayer({
        source: source,
        style: {
            'fill-color': 'rgba(255, 255, 255, 0.2)',
            'stroke-color': '#ffcc33',
            'stroke-width': 2,
            'circle-radius': 7,
            'circle-fill-color': '#ffcc33',
        },
    });
      
    useEffect(() => {
        const map = new Map({
            target: "map",
            layers: [
                new TileLayer({
                    source: new OSM()
                }),
                vector,
                // new TileLayer({
                //     source: new WMTS({
                //         // Base URL from GetCapabilities 'GetTile' operation xlink:href
                //         // Append username/password as query parameters
                //         url: 'https://services.datafordeler.dk/DKskaermkort/topo_skaermkort_daempet/1.0.0/Wmts?username=STGGAEECCJ&password=een!oM8HJ7_!aCw6',
                //         layer: 'topo_skaermkort_daempet',
                //         matrixSet: 'View1',
                //         format: 'image/jpeg',
                //         projection: proj!,
                //         tileGrid: new WMTSTileGrid({
                //             origin: origin, // Use the precise origin from capabilities
                //             resolutions: resolutions,
                //             matrixIds: matrixIds,
                //             tileSize: tileSize, // Explicitly set tile size
                //         }),
                //         style: 'default',
                //         wrapX: true, // Set to true if tiles wrap horizontally across the globe (common)
                //     }),
                // })
            ],
            view: new View({
                projection: proj!,
                // Set center and zoom according to your needs within the new projection extent
                // A good starting center could be the middle of the projection extent
                center: [700811.1296944167,6169212.693143044],
                zoom: 10, // Start at zoom 0 or adjust based on desired initial view
                extent: projectionExtent, // Constrain the view to the projection's extent
            }),
        });

        return () => {
            map.setTarget(undefined);
        };
    }, []);
    
    const modify = new Modify({source: source});
    map.addInteraction(modify);

    let draw, snap; // global so we can remove them later
    const typeSelect = document.getElementById('type');

    function addInteractions() {
    draw = new Draw({
        source: source,
        type: typeSelect.value,
    });
    map.addInteraction(draw);
    snap = new Snap({source: source});
    map.addInteraction(snap);
    }

    /**
     * Handle change event.
     */
    typeSelect.onchange = function () {
    map.removeInteraction(draw);
    map.removeInteraction(snap);
    addInteractions();
    };

    addInteractions();
    return (
        <div>
            <div id="polygon" style={{width: "50px", height: "30px"}}>Draw</div>
            <div id="map" style={{ width: "100%", height: "100vh" }} />
        </div>
        
    );
}

export default MapView;