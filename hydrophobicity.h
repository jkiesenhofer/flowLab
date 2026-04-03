dimensionedScalar k
(
    "k",
    dimensionSet( 0, 2, -1, 0, 0, 0, 0),
    scalar(4e-05)
);


volVectorField hydrophobicity
(
IOobject
(
    "hydrophobicity",
    runTime.name(),
    mesh,
    IOobject::READ_IF_PRESENT,
    IOobject::AUTO_WRITE
),
//fvc::grad(sqr(mesh.C().component(vector::X)) + sqr(mesh.C().component(vector::Y)))


1000*fvc::grad(sqr(mesh.C().component(vector::X)) + sqr(mesh.C().component(vector::Y)))
//sqr(mesh.C().component(vector::X))+sqr(mesh.C().component(vector::Y))
);

//phi = fvc::interpolate(hydrophobicity) & mesh.Sf();
//phi = mesh.Sf() & hydrophobicity
//hydrophobicity.internalField() = U.internalField().component(vector::X);


//UU = 1000*fvc::grad(sqr(mesh.C().component(vector::X)) + sqr(mesh.C().component(vector::Y)))/dimTime;


// Create scalar field phi
surfaceScalarField phi
(
    IOobject
    (
        "phi",
        runTime.name(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    fvc::interpolate(hydrophobicity) & mesh.Sf()
);


volVectorField surfaceEnergy
(
    IOobject
    (
        "surfaceEnergy",
        runTime.name(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
1000*fvc::grad(sqr(mesh.C().component(vector::X)) + sqr(mesh.C().component(vector::Y)))
);

//UU = div(fvc::interpolate(hydrophobicity) & mesh.Sf());


/*
volScalarField UU
(
IOobject
(
    "UU",
    runTime.name(),
    mesh,
    IOobject::READ_IF_PRESENT,
    IOobject::AUTO_WRITE
),
    fvc::div(phi,hydrophobicity)
);

*/


volVectorField U
(
    IOobject
    (
        "U",
        runTime.name(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    mesh,
    dimensionedVector("zero", dimVelocity, vector(0,0,0))
);

vector m(5,0,0); // dipole moment along x

forAll(U, celli)
{
    vector r = mesh.C()[celli];
    scalar rMag = mag(r);
    if (rMag > SMALL)
        U[celli] = (m - 3*(m & r)*r/(rMag*rMag))/(rMag*rMag*rMag);
}


//#include "createFields.H"


//volVectorField hydrophobicity = U.component(vector::X);

// Create scalar field phi
volScalarField AB
(
    IOobject
    (
        "AB",
        runTime.name(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
   fvc::average(phi)
    
);

