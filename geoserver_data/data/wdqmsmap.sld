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
         <Name>not in vola</Name>
		   <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>invola</ogc:PropertyName>
			   <ogc:Literal>false</ogc:Literal>
             </ogc:PropertyIsEqualTo>
             
          
          </ogc:Filter>
                 <LineSymbolizer>
         <Stroke>
           <CssParameter name="stroke">#e5e600</CssParameter>
           <CssParameter name="stroke-width">2</CssParameter>
           <CssParameter name="stroke-dasharray">5 2</CssParameter>
         </Stroke>
       </LineSymbolizer>
		</Rule>
	  
        
        <Rule>
         <Name>black</Name>
		   <ogc:Filter>
             <And>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>0.0</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               
             </And>
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
         <Name>red</Name>
		   <ogc:Filter>
             <And>
              <ogc:PropertyIsLessThan>
			   <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>0.30</ogc:Literal>
			  </ogc:PropertyIsLessThan>
             <ogc:PropertyIsGreaterThan>
               <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>0.0</ogc:Literal>
             </ogc:PropertyIsGreaterThan>
               
             </And>
               </ogc:Filter>
           <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
                 <Fill><CssParameter name="fill">#ff3300</CssParameter></Fill>
			   </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>
	  <Rule>
         <Name>orange</Name>
		   <ogc:Filter>
             <And>
			 <ogc:PropertyIsLessThan>
			   <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>0.80</ogc:Literal>
			 </ogc:PropertyIsLessThan>
             <ogc:PropertyIsGreaterThanOrEqualTo>
   			   <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>0.80</ogc:Literal>
             </ogc:PropertyIsGreaterThanOrEqualTo>
			   
             </And>
           </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">#ff9900</CssParameter></Fill>
               </Mark>
                          <Size>8</Size>

			 </Graphic>
		   </PointSymbolizer>
		</Rule>

		
 <Rule>
         <Name>green</Name>
		   <ogc:Filter>
             <And>
			 <ogc:PropertyIsGreaterThan>
			   <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>0.80</ogc:Literal>
			 </ogc:PropertyIsGreaterThan>			   
             <ogc:PropertyIsLessThan>
			   <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>1.1</ogc:Literal>
			 </ogc:PropertyIsLessThan>			   
             
             </And>
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
         <Name>pink</Name>
		   <ogc:Filter>
             <And>
			 <ogc:PropertyIsGreaterThanOrEqualTo>
			   <ogc:PropertyName>per_received</ogc:PropertyName>
			   <ogc:Literal>100</ogc:Literal>
			 </ogc:PropertyIsGreaterThanOrEqualTo>			   
             
             </And>
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

        
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>