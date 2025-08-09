"use client";
import { Map, View } from "ol";
import Draw from 'ol/interaction/Draw.js';
import Modify from 'ol/interaction/Modify.js';
import Snap from 'ol/interaction/Snap.js';
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import "ol/ol.css";
import { get as getProjection } from "ol/proj";
import { register } from 'ol/proj/proj4';
import { OSM } from "ol/source";
import VectorSource from "ol/source/Vector";
import proj4 from 'proj4';
import { useEffect, useState, useRef, useMemo } from "react";
import AnalysisTab from './analysis-tab';
import ResultsViewer from './results-viewer';

function MapView() {
    const [isAnalysisTabVisible, setIsAnalysisTabVisible] = useState(false);
    const [isResultsViewerVisible, setIsResultsViewerVisible] = useState(false);
    const [polygonBbox, setPolygonBbox] = useState<number[] | null>(null);
    const [currentMode, setCurrentMode] = useState<'Pan' | 'Polygon'>('Pan');
    const mapRef = useRef<Map | null>(null);
    const sourceRef = useRef<VectorSource | null>(null);

    // 1. Projection Definition (from previous setup, confirmed by capabilities)
    const projectionCode = 'EPSG:25832';
    const projectionDefinition = '+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs';
    proj4.defs(projectionCode, projectionDefinition);
    register(proj4 as unknown as typeof import('proj4'));

    const proj = getProjection(projectionCode);

    // 2. Projection Extent (from <ows:BoundingBox> in GetCapabilities)
    const projectionExtent = useMemo(() => [120000, 5900000, 1000000, 6500000], []);

    // 3. Tile Grid Origin (from <TopLeftCorner> in GetCapabilities)
    // Note: OpenLayers getTopLeft(extent) can be used if origin == top-left of extent.
    // However, the GetCapabilities explicitly states TopLeftCorner for the TileMatrixSet.
    // const origin = [120000.000000, 6500000.000000]; // This is (minX, maxY)

    // 4. Resolutions (calculated from ScaleDenominator in GetCapabilities)
    // Using the formula: Resolution = ScaleDenominator / 90.71428571428571 (common for web maps)
    // const resolutions = [
    //     64500.0,
    //     32250.0,
    //     16125.0,
    //     8062.5,
    //     4031.25,
    //     2015.625,
    //     1007.8125,
    //     503.90625,
    //     251.953125,
    //     125.9765625,
    //     62.98828125,
    //     31.494140625,
    //     15.7470703125,
    //     7.87353515625,
    // ];

    // 5. Matrix IDs (from <ows:Identifier> under each <TileMatrix>)
    // These correspond to your zoom levels 0-13.
    // const matrixIds = [
    //     '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13'
    // ];

    // 6. Tile Size (from <TileWidth> and <TileHeight> in GetCapabilities)
    // It's 256x256, which is OpenLayers default, but good to be explicit.
    // const tileSize = 256;

    const source = useMemo(() => {
        const s = new VectorSource();
        sourceRef.current = s;
        return s;
    }, []);
    
    const vector = useMemo(() => new VectorLayer({
        source: source,
        style: {
            'fill-color': 'rgba(255, 255, 255, 0.2)',
            'stroke-color': '#ffcc33',
            'stroke-width': 2,
            'circle-radius': 7,
            'circle-fill-color': '#ffcc33',
        },
    }), [source]);
      
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
                zoom: 12, // Start at zoom 0 or adjust based on desired initial view
                extent: projectionExtent, // Constrain the view to the projection's extent
            }),
        });
        const modify = new Modify({source: source});
        
        // Add event listener to capture coordinates when polygon is modified
        modify.on('modifyend', function(event) {
            const features = event.features;
            features.forEach(function(feature) {
                const geometry = feature.getGeometry();
                if (geometry) {
                    const extent = geometry.getExtent();
                    console.log('Modified polygon bounding box:', extent);
                }
            });
        });
        
        map.addInteraction(modify);
        mapRef.current = map;
        
 
        return () => {
            map.setTarget(undefined);
        };
    }, [proj, projectionExtent, source, vector]);

    // Effect to handle mode changes
    useEffect(() => {
        if (mapRef.current && sourceRef.current) {
            const map = mapRef.current;
            const source = sourceRef.current;
            
            // Remove existing Draw and Snap interactions
            map.getInteractions().getArray().slice().forEach((interaction: unknown) => {
                if (interaction instanceof Draw || interaction instanceof Snap) {
                    map.removeInteraction(interaction);
                }
            });
            
            // Add new interactions based on mode
            if (currentMode === "Polygon") {
                const draw = new Draw({
                    source: source,
                    type: "Polygon",
                });
                
                draw.on('drawend', function(event) {
                    const feature = event.feature;
                    const geometry = feature.getGeometry();
                    if (geometry) {
                        const extent = geometry.getExtent();
                        console.log('Polygon bounding box:', extent);
                        
                        setPolygonBbox(extent);
                        setIsAnalysisTabVisible(true);
                    }
                });
                
                map.addInteraction(draw);
                const snap = new Snap({source: source});
                map.addInteraction(snap);
            }
        }
    }, [currentMode]);

    
    return (
        <div style={{width: "100%", height: "100vh"}}>
            <div id="map" style={{ width: "100%", height: "100vh" }} />
            
            {/* Floating Mode Buttons - Left Side */}
            <div className="fixed left-4 top-1/2 transform -translate-y-1/2 flex flex-col gap-3 z-40">
                <button
                    onClick={() => setCurrentMode('Pan')}
                    className={`p-3 rounded-full shadow-lg transition-colors ${
                        currentMode === 'Pan' 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-white text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Pan Mode"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                    </svg>
                </button>
                
                <button
                    onClick={() => setCurrentMode('Polygon')}
                    className={`p-3 rounded-full shadow-lg transition-colors ${
                        currentMode === 'Polygon' 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-white text-gray-700 hover:bg-gray-100'
                    }`}
                    title="Draw Polygon Mode"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                </button>
            </div>
            
            {/* Floating Results Button */}
            <button
                onClick={() => setIsResultsViewerVisible(true)}
                className="fixed bottom-4 left-4 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg z-40"
                title="View Analysis Results"
            >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            </button>

            <AnalysisTab 
                isVisible={isAnalysisTabVisible}
                onClose={() => setIsAnalysisTabVisible(false)}
                polygonBbox={polygonBbox}
            />
            
            <ResultsViewer 
                isVisible={isResultsViewerVisible}
                onClose={() => setIsResultsViewerVisible(false)}
            />
        </div>
        
    );
}

export default MapView;