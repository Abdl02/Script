package com.digitinary.dgate.model.monetization;

import com.digitinary.dgate.model.apispec.ApiSpec;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;
import java.util.ArrayList;
import java.util.List;

/**
 * ProductSimpleView Model.
 *
 * @author Raad khatatbeh
 * @since 20/10/2024
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
@Data
public class ProductSimpleViewModel {

    private Long productId;
    private String name;
    private String desc;
    private ProductStatus status;

    private List<ApiSpec> apiSpecs = new ArrayList<>();
}
