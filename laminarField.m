% 2d Laminar flow
clear; clc;

% Gitter
nx = 41; ny = 41;
Lx = 1; Ly = 1;
dx = Lx/(nx-1);
dy = Ly/(ny-1);

% Parameter
rho = 1000;
nu = 1e-3;
dt = 0.001;
nt = 8;

% Fields
u = zeros(ny,nx);
v = zeros(ny,nx);
p = ones(ny,nx)*1e+5;

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

    % Boundaries
    u(20:end,end-20) = -2;
    %v(25:30,17:25) = 7; % m/s
    %v(:,end-20:end) = 7;
    %p(17:25,17:25) = 2e+5;% p(end,:) = rand; N/m^2
    p(17:25,17:25) = 1.3e+5;
    %p(10:15,10:15) = rand;
end
speed = sqrt(u.^2 + v.^2);
Re=rho * speed .* Lx / nu;
div = u./dx + v./dy;
%Re=Re/max(max(Re));

%subplot(1,2,1)
%contourf(Re)
%colorbar
%xlabel('x')
%ylabel('y')

%subplot(1,2,2)
contourf(speed)
%quiver(u,v)
xlim([0 nx])
ylim([0 ny])
colorbar
xlabel('x')
ylabel('y')
axis equal
