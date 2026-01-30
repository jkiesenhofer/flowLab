% 2d Laminar flow
clear; clc;

% Gitter
nx = 41; ny = 41;
Lx = 1; Ly = 1;
dx = Lx/(nx-1);
dy = Ly/(ny-1);

% Parameter
rho = 1;
nu = 0.1;
dt = 0.001;
nt = 500;

% Fields
u = zeros(ny,nx);
v = zeros(ny,nx);
p = zeros(ny,nx);

for n = 1:nt
    un = u;
    vn = v;

    % Velocity updates
    u(2:end-1,2:end-1) = un(2:end-1,2:end-1) ...
        - dt/dx * un(2:end-1,2:end-1) .* (un(2:end-1,2:end-1) - un(2:end-1,1:end-2)) ...
        - dt/dy * vn(2:end-1,2:end-1) .* (un(2:end-1,2:end-1) - un(1:end-2,2:end-1)) ...
        - dt/(2*rho*dx) * (p(2:end-1,3:end) - p(2:end-1,1:end-2)) ...
        + nu * (dt/dx^2 * (un(2:end-1,3:end) - 2*un(2:end-1,2:end-1) + un(2:end-1,1:end-2)) ...
        + dt/dy^2 * (un(3:end,2:end-1) - 2*un(2:end-1,2:end-1) + un(1:end-2,2:end-1)));

    v(2:end-1,2:end-1) = vn(2:end-1,2:end-1) ...
        - dt/dx * un(2:end-1,2:end-1) .* (vn(2:end-1,2:end-1) - vn(2:end-1,1:end-2)) ...
        - dt/dy * vn(2:end-1,2:end-1) .* (vn(2:end-1,2:end-1) - vn(1:end-2,2:end-1)) ...
        - dt/(2*rho*dy) * (p(3:end,2:end-1) - p(1:end-2,2:end-1)) ...
        + nu * (dt/dx^2 * (vn(2:end-1,3:end) - 2*vn(2:end-1,2:end-1) + vn(2:end-1,1:end-2)) ...
        + dt/dy^2 * (vn(3:end,2:end-1) - 2*vn(2:end-1,2:end-1) + vn(1:end-2,2:end-1)));

    % Boundaries (Cavity)
    u(:,1) = 0; u(:,end) = 0;
    u(1,:) = 0; u(end,:) = 1;   % moving lid
    v(:,:) = 0;

    % Plot
    if mod(n,50)==0
        quiver(u,v)
        title(['t = ',num2str(n*dt)])
        drawnow
    end
end
