theta = linspace(0,2*pi,200);

r_base = 1;
r_distort = 0.2*sin(3*theta) + 0.1*cos(5*theta);

r = r_base + r_distort;

x = r .* cos(theta);
y = r .* sin(theta);

figure
fill(x,y,[0.15 0.7 0.5])
axis equal

subplot(1,2,1)
fill(x,y,[0.15 0.7 0.5])
axis equal
xlim([-2 2])
ylim([-2 2])

x = r .* cos(theta)/2;
y = r .* sin(theta)/2+1;

subplot(1,2,2)
fill(x,y,[0.15 0.7 0.5])
axis equal

xlim([-2 2])
ylim([-2 2])
