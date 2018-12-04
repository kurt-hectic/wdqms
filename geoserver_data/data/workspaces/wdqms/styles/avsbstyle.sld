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
      <Title>compare two NWP centerd</Title>
      <Abstract>comparing two NWP centers</Abstract>
      <FeatureTypeStyle>
	  
	  <Rule>
         <Name>Same</Name>
		  <ogc:Filter>
             <ogc:PropertyIsEqualTo>
               <ogc:PropertyName>diff_per_received</ogc:PropertyName>
			   <ogc:Literal>0</ogc:Literal>
             </ogc:PropertyIsEqualTo>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill>
                   <CssParameter name="fill"><ogc:Function name="env">
   					<ogc:Literal>same_color</ogc:Literal>
                     </ogc:Function>
                     </CssParameter>
                   <CssParameter name="fill-opacity">
                   <ogc:Function name="env">
   					<ogc:Literal>same_opacity</ogc:Literal>
                    </ogc:Function>
                   </CssParameter>

                 </Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>
        
         <Rule>
         <Name>Have more</Name>
		  <ogc:Filter>
             <ogc:PropertyIsGreaterThan>
               <ogc:PropertyName>diff_per_received</ogc:PropertyName>
			   <ogc:Literal>0</ogc:Literal>
             </ogc:PropertyIsGreaterThan>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">
                   <ogc:Function name="env">
   					<ogc:Literal>more_color</ogc:Literal>
                    </ogc:Function>
                   </CssParameter></Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>

        <Rule>
         <Name>Have less</Name>
		  <ogc:Filter>
             <ogc:PropertyIsLessThan>
               <ogc:PropertyName>diff_per_received</ogc:PropertyName>
			   <ogc:Literal>0</ogc:Literal>
             </ogc:PropertyIsLessThan>
               </ogc:Filter>
		   <PointSymbolizer>
			 <Graphic>
			   <Mark>
                 <WellKnownName>circle</WellKnownName>
				 <Fill><CssParameter name="fill">
                   <ogc:Function name="env">
   					<ogc:Literal>less_color</ogc:Literal>
   				   </ogc:Function> 
                  </CssParameter></Fill>
               </Mark>
              <Size>8</Size>
			 </Graphic>
		   </PointSymbolizer>
		</Rule>



      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>