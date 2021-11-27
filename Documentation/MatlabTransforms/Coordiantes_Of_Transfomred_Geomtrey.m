%define fig and axes
hFig=figure;
hAx=axes('parent',hFig);
xlim(hAx,[-10,10]); ylim(hAx,[-10,10]);
grid(hAx,'on'); axis(hAx,'equal'); hold(hAx,'on');

%define transform 
hTransform=hgtransform('parent',hAx);
Color=[1,0,0];
x=[-1,1,1,-1];
y=[-1,-1,1,1];
hPatch=patch(x,y,Color,'parent',hTransform);

disp('Initial Vertices of Patch')
disp(hPatch.Vertices);

%Rotate transform by 30 degrees
R=makehgtform('zrotate',deg2rad(30));
hTransform.Matrix=R;
drawnow;

disp('Rotated Vertices of Patch')
disp(hPatch.Vertices);
disp('Something went wrong... these are the initial coordiantes!')
disp('workaround solution:')

%get transformed coordiants via matrix multiplication
hPatch=hTransform.Children(1);
m=size(hPatch.Vertices,1); %amount of vertices
HomogOrdinates=[hPatch.Vertices,zeros(m,1),ones(m,1)]; %[x,y,z,1]
WorldOrdinates=hTransform.Matrix*HomogOrdinates'; %notice the transpose!
world_x=WorldOrdinates(1,:);
world_y=WorldOrdinates(2,:);

scatter(hAx,world_x,world_y,100,[0,0,1],'*');

disp('Rotated Vertices of Patch');
disp([world_x;world_y]');
disp('ahhhh much better');