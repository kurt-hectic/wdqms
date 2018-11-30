<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- a Named Layer is the basic building block of an SLD document -->
  <NamedLayer>
    <Name>default_point</Name>
    <UserStyle>
    <!-- Styles can have names, titles and abstracts -->
      <Title>Default Point</Title>
      <Abstract>A sample style that draws a point</Abstract>
      <!-- FeatureTypeStyles describe how to render different features -->
      <!-- A FeatureTypeStyle for rendering points -->
      <FeatureTypeStyle>
        <Rule>
          <Name>rule1</Name>
          <Title>Red circle</Title>
          <Abstract>A 6 pixel square with a red fill and no stroke</Abstract>
             <ogc:Filter>
               <ogc:PropertyIsEqualTo>
                 <ogc:PropertyName>stationtype2</ogc:PropertyName>
                 <ogc:Literal>1</ogc:Literal>
               </ogc:PropertyIsEqualTo>
   			</ogc:Filter>
          
          <PointSymbolizer>
              <Graphic>
                <Mark>
                  <WellKnownName>circle</WellKnownName>
                  <Fill>
                    <CssParameter name="fill">#FF0000</CssParameter>
                  </Fill>
                </Mark>
              <Size>3</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
                <Rule>
          <Name>rule2</Name>
          <Title>blue circle</Title>
          <Abstract>A 6 pixel square with a red fill and no stroke</Abstract>
             <ogc:Filter>
               <ogc:PropertyIsEqualTo>
                 <ogc:PropertyName>stationtype2</ogc:PropertyName>
                 <ogc:Literal>2</ogc:Literal>
               </ogc:PropertyIsEqualTo>
   			</ogc:Filter>
          
          <PointSymbolizer>
              <Graphic>
                <Mark>
                  <WellKnownName>circle</WellKnownName>
                  <Fill>
                    <CssParameter name="fill">#0000ff</CssParameter>
                  </Fill>
                </Mark>
              <Size>3</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>

              <Rule>
          <Name>rule3</Name>
          <Title>green circle</Title>
          <Abstract>A 6 pixel square with a red fill and no stroke</Abstract>
             <ogc:Filter>
               <ogc:PropertyIsEqualTo>
                 <ogc:PropertyName>stationtype2</ogc:PropertyName>
                 <ogc:Literal>3</ogc:Literal>
               </ogc:PropertyIsEqualTo>
   			</ogc:Filter>
          
          <PointSymbolizer>
              <Graphic>
                <Mark>
                  <WellKnownName>circle</WellKnownName>
                  <Fill>
                    <CssParameter name="fill">#009933</CssParameter>
                  </Fill>
                </Mark>
              <Size>3</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        
         <Rule>
          <Name>rule4</Name>
          <Title>pink circle</Title>
          <Abstract>A 6 pixel square with a red fill and no stroke</Abstract>
             <ogc:Filter>
               <ogc:PropertyIsEqualTo>
                 <ogc:PropertyName>stationtype2</ogc:PropertyName>
                 <ogc:Literal>4</ogc:Literal>
               </ogc:PropertyIsEqualTo>
   			</ogc:Filter>
          
          <PointSymbolizer>
              <Graphic>
                <Mark>
                  <WellKnownName>circle</WellKnownName>
                  <Fill>
                    <CssParameter name="fill">#cc0099</CssParameter>
                  </Fill>
                </Mark>
              <Size>3</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>

              <Rule>
          <Name>rule5</Name>
          <Title>yellow circle</Title>
          <Abstract>A 6 pixel square with a red fill and no stroke</Abstract>
             <ogc:Filter>
               <ogc:PropertyIsEqualTo>
                 <ogc:PropertyName>stationtype2</ogc:PropertyName>
                 <ogc:Literal>5</ogc:Literal>
               </ogc:PropertyIsEqualTo>
   			</ogc:Filter>
          
          <PointSymbolizer>
              <Graphic>
                <Mark>
                  <WellKnownName>circle</WellKnownName>
                  <Fill>
                    <CssParameter name="fill">#ffff00</CssParameter>
                  </Fill>
                </Mark>
              <Size>3</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>