
function init_grid_world(gridScale, scene) //minx, miny, minz, maxx, maxy, maxz)
{
	// Limit minimum grid world size
	// TODO 
	
	
	
	var light = new THREE.DirectionalLight(0xFFFFFF);
	light.position.set(0, 10, 10);
	light.castShadow = true;
	scene.add( light );
	
	// SKYBOX
	var skyBoxGeometry = new THREE.CubeGeometry( 10000, 10000, 10000 );
	var skyBoxMaterial = new THREE.MeshBasicMaterial( { color: 0xBBDDFF, side: THREE.BackSide } );
	var skyBox = new THREE.Mesh( skyBoxGeometry, skyBoxMaterial );
	scene.add(skyBox);
	
	// fog must be added to scene before first render
	//scene.fog = new THREE.FogExp2( 0x9999ff, 0.00025 );
	
	// Floor
	var floor_geometry = new THREE.BoxGeometry(25, 2, 25);
	var floor_mat = new THREE.MeshBasicMaterial( {color: 0xC0C0C0} );
	var floor_mesh = new THREE.Mesh( floor_geometry, floor_mat );
	floor_mesh.position.y = -1.01;
	scene.add( floor_mesh );
	
	// Floor grid
	var grid_xz = new THREE.GridHelper(25, 25 / gridScale, 0x555555, 0x777777 );
	//grid_xz.position.set( 25, 0, 25);
	scene.add( grid_xz );
	
	// Wall grid 1 yz
	var grid_yz = new THREE.GridHelper(25, 25 / gridScale, 0x555555, 0x666666 );
	grid_yz.rotation.z = Math.PI/2;
	grid_yz.position.set(-25/2, 25/2, 0);
	scene.add( grid_yz );
	
	// Wall grid 2 xy
	var grid_xy = new THREE.GridHelper(25, 25 / gridScale, 0x555555, 0x666666 );
	grid_xy.rotation.x = Math.PI/2;
	grid_xy.position.set(0, 25/2, -25/2);
	scene.add( grid_xy );
	
}

function NewQuadArm() {
	var arm = new THREE.Mesh( new THREE.BoxGeometry(0.20, 0.01, 0.03),
							new THREE.MeshStandardMaterial(
							{color: 0x777777, metalness: 0.3, roughness: 0.2} ));
	var motor = new THREE.Mesh( new THREE.CylinderGeometry(0.015, 0.015, 0.02),
							new THREE.MeshStandardMaterial(
							{color: 0x444444, metalness: 0.9, roughness: 0.2} ));
	arm.add( motor );
	motor.position.set(0.10 - 0.015, 0.015, 0);
	var propeller = new THREE.Mesh( new THREE.BoxGeometry(0.18, 0.005, 0.02),
							new THREE.MeshStandardMaterial(
							{color: 0x7777DD, metalness: 0.2, roughness: 0.7} ));
	motor.add( propeller );
	propeller.position.set(0, 0.015, 0);
	return {arm: arm, propeller: propeller};
}

function NewQuadcopter()
{
	var bottom_base = new THREE.Mesh( new THREE.BoxGeometry(0.30, 0.02, 0.05),
		new THREE.MeshStandardMaterial( {color: 0x777777, metalness: 0.3, roughness: 0.2} ));
	scene.add(bottom_base);
	var mid_base = new THREE.Mesh( new THREE.BoxGeometry(0.20, 0.03, 0.04),
		new THREE.MeshLambertMaterial( {color: 0x990000, transparent: true, opacity: 0.9} ));
	bottom_base.add(mid_base);
	mid_base.position.set(0.03, 0.025, 0);
	var top_base = new THREE.Mesh( new THREE.BoxGeometry(0.25, 0.02, 0.05),
		new THREE.MeshStandardMaterial( {color: 0x777777, metalness: 0.3, roughness: 0.2} ));
	bottom_base.add(top_base);
	top_base.position.set(0.03, 0.05, 0);
	
	var armFL = NewQuadArm();
	bottom_base.add(armFL.arm);
	armFL.arm.position.set(0.08, 0.0, -0.06);
	armFL.arm.rotation.y = Math.PI / 4;
	
	var armFR = NewQuadArm();
	bottom_base.add(armFR.arm);
	armFR.arm.position.set(0.08, 0.0, 0.06);
	armFR.arm.rotation.y = -Math.PI / 4;
	
	var armRL = NewQuadArm();
	bottom_base.add(armRL.arm);
	armRL.arm.position.set(-0.08, 0.0, -0.06);
	armRL.arm.rotation.y = 3 * Math.PI / 4;
	
	var armRR = NewQuadArm();
	bottom_base.add(armRR.arm);
	armRR.arm.position.set(-0.08, 0.0, 0.06);
	armRR.arm.rotation.y = -3 * Math.PI / 4;
	
	return {base: bottom_base, propFL: armFL.propeller, propFR: armFR.propeller,
								propRL: armRL.propeller, propRR: armRR.propeller};
}

function NewTrajectoryPath(x, y, z, inputColor)
{
	var line_path = new THREE.BufferGeometry();
	var line_positions = new Float32Array( t.length * 3 );
	line_path.addAttribute( 'position', new THREE.BufferAttribute( line_positions, 3) );
	var index=0;
	for (var i=0; i < t.length; i++) {
		line_positions[index++] = x[i];
		line_positions[index++] = y[i];
		line_positions[index++] = z[i];
	}
	var line = new THREE.Line( line_path, new THREE.LineBasicMaterial({color:0x003300}));
	
	return {line: line, path: line_path};
}