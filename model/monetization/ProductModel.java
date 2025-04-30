package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.model.RestrictionType;
import com.digitinary.dgate.model.apispec.ApiSpec;
import com.digitinary.dgate.model.runtimeconfig.RuntimeConfigPublicationModel;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

/**
 * Monetization product model.
 *
 * @author Salah Abu Msameh
 * @since 08/05/2024
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@NoArgsConstructor
@AllArgsConstructor
@Setter
@Getter
@Builder
public class ProductModel {

    private Long productId;
    private String name;
    private String desc;
    private ProductStatus status;
    private String segment;
    private String version;
    private LocalDateTime createdAt;
    private LocalDateTime lastUpdatedAt;
    private boolean premium;
    private RestrictionType restriction;
    private boolean availableOnDevPortal;
    private boolean publishedOnProd;
    private List<ApiSpec> apiSpecs;
    private Set<ProductPlanPriceModel> productPlanPrices;
    private List<AssociatedResource> associatedResources;
    private List<RuntimeConfigPublicationModel> publications;

}
