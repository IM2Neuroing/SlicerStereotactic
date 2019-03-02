
RODS_DIAM = 10;
N_HEIGHT=120;
N_WIDTH=120;
BOX_XLEN=190    ;
BOX_YLEN=190;
BOX_ZLEN=190;

module zFiducial(rodD, nHeight, nWidth){
    diag_len = sqrt(pow(nHeight,2)+pow(nWidth,2));
    nAngle = atan(nWidth/nHeight);
    union(){
        translate([nWidth/2, 0, 0]) cylinder(d=rodD, h=nHeight, center=true, $fn=32);
        translate([-nWidth/2, 0, 0]) cylinder(d=rodD, h=nHeight, center=true, $fn=32);
        translate([0, 0, 0]) 
            rotate([0, -nAngle, 0])  
                cylinder(d=rodD, h=diag_len, center=true, $fn=32);
    }
    translate([nWidth/2, 0, -nHeight/2]) sphere(d=rodD, $fn=32);
    translate([nWidth/2, 0, nHeight/2]) sphere(d=rodD, $fn=32);
    translate([-nWidth/2, 0, -nHeight/2]) sphere(d=rodD, $fn=32);
    translate([-nWidth/2, 0, nHeight/2]) sphere(d=rodD, $fn=32);
}

union(){
    translate([0, -BOX_YLEN/2, 0]) 
        zFiducial(rodD=RODS_DIAM, nHeight=N_HEIGHT, nWidth=N_WIDTH);
    translate([0, BOX_YLEN/2, 0]) 
        zFiducial(rodD=RODS_DIAM, nHeight=N_HEIGHT, nWidth=N_WIDTH);
    translate([BOX_XLEN/2, 0, 0]) 
        rotate([0,0,90]) 
            zFiducial(rodD=RODS_DIAM, nHeight=N_HEIGHT, nWidth=N_WIDTH);
}

