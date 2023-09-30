import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function onPointerDown(event, camera, scene) {

	// calculate pointer position in normalized device coordinates
	// (-1 to +1) for both components

	pointer.x = ( event.clientX / window.innerWidth ) * 2 - 1;
	pointer.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

		// update the picking ray with the camera and pointer position
	raycaster.setFromCamera( pointer, camera );

	// calculate objects intersecting the picking ray
	const intersects = raycaster.intersectObjects( scene.children );

	for ( let i = 0; i < intersects.length; i ++ ) {
		//const face = intersects[i].face;
		console.log(intersects[i]);
		// intersects[0].face.color.setHex(0xff0000);ç
		//const geometry1 = intersects[0].object.geometry
		//const count = geometry1.attributes.position.count;
		//geometry1.setAttribute( 'color', new THREE.BufferAttribute( new Float32Array( count * 3 ), 3 ));
		//const color = new THREE.Color( Math.random() * 0xffffff ); // random color
		const face = intersects[0].face;
		const geometry1 = intersects[0].object.geometry;

		const color = new THREE.Color();
		const positions1 = geometry1.attributes.position;
		const colors1 = geometry1.attributes.color;

		const set_color = (i) => {
			color.setHSL(0.9, 0.5, 0.5, THREE.SRGBColorSpace );
			colors1.setXYZ( i, color.r, color.g, color.b );
		}

		set_color(face.a);
		set_color(face.b);
		set_color(face.c);

		geometry1.attributes.color.needsUpdate = true;
	}
}

function main() {
	const canvas = document.querySelector( '#c' );
	const renderer = new THREE.WebGLRenderer( { antialias: true, canvas } );

	const fov = 45;
	const aspect = 2; // the canvas default
	const near = 0.1;
	const far = 100;
	const camera = new THREE.PerspectiveCamera( fov, aspect, near, far );
	camera.position.set( 0, 10, 0 );
	const controls = new OrbitControls( camera, canvas );
	controls.target.set( 0, 5, 0 );
	controls.update();

	const scene = new THREE.Scene();
	scene.background = new THREE.Color( 'black' );

	{

		const skyColor = 0xB1E1FF; // light blue
		const groundColor = 0xB97A20; // brownish orange
		const intensity = 2;
		const light = new THREE.HemisphereLight( skyColor, groundColor, intensity );
		scene.add( light );

	}

	{

		const color = 0xFFFFFF;
		const intensity = 2.5;
		const light = new THREE.DirectionalLight( color, intensity );
		light.position.set( 0, 10, 0 );
		light.target.position.set( - 5, 0, 0 );
		scene.add( light );
		scene.add( light.target );

	}

	{

		const objLoader = new OBJLoader();
		objLoader.load( '/public/monkey.obj', ( root ) => {

				const geometry1 = root.children[0].geometry;

				const count = geometry1.attributes.position.count;
				geometry1.setAttribute( 'color', new THREE.BufferAttribute( new Float32Array( count * 3 ), 3 ) );

				const color = new THREE.Color();
				const positions1 = geometry1.attributes.position;
				const colors1 = geometry1.attributes.color;

				const material = new THREE.MeshPhongMaterial( {
					color: 0xffffff,
					flatShading: true,
					vertexColors: true,
					shininess: 0
				} );

				for ( let i = 0; i < count; i ++ ) {
					//color.setHSL(positions1.getX(i)/positions1.getY(i), 1000, 0.5, THREE.SRGBColorSpace );
					colors1.setXYZ( i, 1, 1, 1);
				}

				const wireframeMaterial = new THREE.MeshBasicMaterial( { color: 0x000000, wireframe: true, transparent: true } );
				let mesh = new THREE.Mesh( geometry1, material );
				let wireframe = new THREE.Mesh( geometry1, wireframeMaterial );
				mesh.add( wireframe );
				scene.add( mesh );
		} );
	}

	function resizeRendererToDisplaySize( renderer ) {

		const canvas = renderer.domElement;
		const width = canvas.clientWidth;
		const height = canvas.clientHeight;
		const needResize = canvas.width !== width || canvas.height !== height;
		if ( needResize ) {

			renderer.setSize( width, height, false );

		}

		return needResize;

	}

	function render() {

		if ( resizeRendererToDisplaySize( renderer ) ) {

			const canvas = renderer.domElement;
			camera.aspect = canvas.clientWidth / canvas.clientHeight;
			camera.updateProjectionMatrix();

		}

		renderer.render( scene, camera );

		requestAnimationFrame( render );

	}

	addEventListener( 'pointerdown', (event) => onPointerDown(event, camera, scene) );
	requestAnimationFrame( render );

}

main();