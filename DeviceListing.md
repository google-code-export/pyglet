| Device   | Works? | Notes |
|:---------|:-------|:------|
| GeForce| yes  | All GeForce devices work but make sure your drivers are up to date |
| ATI      | poor | OpenGL is just not well-supported under Linux and Windows. All ATI devices have issues including corruption and crashing. ATI under OS X is better-supported |
| Intel GMA 900 | partial | Doesn't support VSYNC or hardware shaders |
| Intel GMA 950 | partial | Doesn't support hardware shaders |
| S3 GRAPHICS ProSavageDDR | poor | OpenGL is just not well-supported. |
VSYNC: you will need to set the environment variable PYGLET\_VSYNC=no