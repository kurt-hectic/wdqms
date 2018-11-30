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
      <Title>percentage received map</Title>
      <Abstract>color points according to percent received</Abstract>
      <FeatureTypeStyle>
        <Rule>
         <Name>black</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>nr_received</ogc:PropertyName>
			   <ogc:Literal>0</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
           <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill><CssParameter name="fill">#000000</CssParameter></Fill>
			   </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>
	  
	  <Rule>
         <Name>blue</Name>
		   <ogc:Filter>
              <ogc:PropertyIsEqualTo>
			   <ogc:PropertyName>nr_received</ogc:PropertyName>
			   <ogc:Literal>1</ogc:Literal>
			  </ogc:PropertyIsEqualTo>
               </ogc:Filter>
           <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill><CssParameter name="fill">#0000CD</CssParameter></Fill>
			   </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>
	  <Rule>
         <Name>green</Name>
		   <ogc:Filter>
             <ogc:And>
			 <ogc:PropertyIsGreaterThan>
			   <ogc:PropertyName>nr_received</ogc:PropertyName>
			   <ogc:Literal>1</ogc:Literal>
			 </ogc:PropertyIsGreaterThan>
             <ogc:PropertyIsLessThan>
   			   <ogc:PropertyName>percentage_received</ogc:PropertyName>
			   <ogc:Literal>100</ogc:Literal>
             </ogc:PropertyIsLessThan>
			   
             </ogc:And>
           </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#009900</CssParameter></Fill>
               </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>

		
 <Rule>
         <Name>green (top)</Name>
		   <ogc:Filter>
             
             <ogc:PropertyIsEqualTo>
			   <ogc:PropertyName>percentage_received</ogc:PropertyName>
			   <ogc:Literal>100</ogc:Literal>
			 </ogc:PropertyIsEqualTo>			   
             
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#00FF00</CssParameter></Fill>
                       </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>
 <Rule>
         <Name>pink</Name>
		   <ogc:Filter>
             <ogc:And>
             <ogc:PropertyIsGreaterThan>
			   <ogc:PropertyName>percentage_received</ogc:PropertyName>
			   <ogc:Literal>100</ogc:Literal>
			 </ogc:PropertyIsGreaterThan>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>invola</ogc:PropertyName>
			   <ogc:Literal>true</ogc:Literal>
             </ogc:PropertyIsEqualTo>

             </ogc:And>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#ff33cc</CssParameter></Fill>
               </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>
        
         <Rule>
         <Name>not in vola</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>invola</ogc:PropertyName>
			   <ogc:Literal>false</ogc:Literal>
             </ogc:PropertyIsEqualTo>
             
          
          </ogc:Filter>
          <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill><CssParameter name="fill">#FFFF33</CssParameter></Fill>
                 <!--			     
                 <Stroke>
                    <CssParameter name="stroke">#0000FF</CssParameter>

                   <CssParameter name="stroke">#333333</CssParameter>
                   <CssParameter name="stroke-width">1</CssParameter>
                 </Stroke>
				-->
                 
               </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
          
		</Rule>

        
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>